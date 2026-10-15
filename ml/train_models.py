"""Reproducibly train the FakeGuard Instagram and Twitter classifiers.

Twitter training intentionally uses only ``twitter1``: it is the only bundled
source that contains both the four supported inference features and a label.
``twitter2`` contains labels but no matching feature records, so it must not be
joined by row order or used to relabel ``twitter1``.
"""
import argparse
import json
import os
import pickle
import sys

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

RANDOM_STATE = 42
INSTA_FEATURE_COLUMNS = ['profile pic', 'nums/length username', 'fullname words', 'nums/length fullname', 'name==username', 'description length', 'external URL', 'private', '#posts', '#followers', '#follows']
INSTA_FEATURE_DISPLAY = ['Profile Pic', 'Nums in Username', 'Fullname Words', 'Nums in Fullname', 'Name == Username', 'Description Length', 'External URL', 'Private Account', 'Posts Count', 'Followers', 'Following']
TWITTER_FEATURE_COLUMNS = ['Retweet Count', 'Mention Count', 'Follower Count', 'Verified']
TWITTER_FEATURE_DISPLAY = ['Retweet Count', 'Mention Count', 'Follower Count', 'Verified']


def metrics_from_predictions(y_true, y_pred, y_probability):
    """Compute all binary metrics with label 1 consistently meaning bot/fake."""
    return {
        'accuracy': round(float(accuracy_score(y_true, y_pred)), 4),
        'precision': round(float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)), 4),
        'recall': round(float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)), 4),
        'f1_score': round(float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)), 4),
        'auc_roc': round(float(roc_auc_score(y_true, y_probability)), 4),
        'confusion_matrix': confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
    }


def validate_twitter_frame(raw):
    """Map the documented Twitter schema and reject incomplete/invalid labels."""
    required = TWITTER_FEATURE_COLUMNS + ['Bot Label']
    missing = sorted(set(required) - set(raw.columns))
    if missing:
        raise ValueError(f'Twitter dataset is missing required columns: {missing}')
    frame = raw.copy().rename(columns={'Bot Label': 'is_fake'})
    frame['Verified'] = frame['Verified'].map({True: 1, False: 0, 'True': 1, 'False': 0, 1: 1, 0: 0})
    for column in TWITTER_FEATURE_COLUMNS + ['is_fake']:
        frame[column] = pd.to_numeric(frame[column], errors='coerce')
    frame = frame.dropna(subset=TWITTER_FEATURE_COLUMNS + ['is_fake']).drop_duplicates()
    frame['is_fake'] = frame['is_fake'].astype(int)
    frame['Verified'] = frame['Verified'].astype(int)
    if set(frame['is_fake'].unique()) != {0, 1}:
        raise ValueError('Twitter labels must contain exactly 0 (human) and 1 (bot).')
    return frame


def load_instagram_data(base_dir):
    paths = [os.path.join(base_dir, 'instagram1', 'Instagram_fake_profile_dataset.csv'), os.path.join(base_dir, 'instagram2', 'train.csv'), os.path.join(base_dir, 'instagram2', 'test.csv')]
    frames = [pd.read_csv(path) for path in paths if os.path.exists(path)]
    if not frames:
        return None
    frame = pd.concat(frames, ignore_index=True).rename(columns={'fake': 'is_fake'}).drop_duplicates()
    frame['follower_ratio'] = frame['#followers'] / frame['#follows'].replace(0, 1)
    return frame


def load_twitter_data(base_dir):
    path = os.path.join(base_dir, 'twitter1', 'bot_detection_data.csv')
    if not os.path.exists(path):
        return None
    frame = validate_twitter_frame(pd.read_csv(path))
    print(f'Twitter samples: {len(frame)}; human={int((frame.is_fake == 0).sum())}; bot={int((frame.is_fake == 1).sum())}')
    return frame


def candidate_models():
    models = {'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_split=5, min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1)}
    if HAS_XGBOOST:
        models['XGBoost'] = XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=RANDOM_STATE, eval_metric='logloss')
    return models


def train_platform_model(df, feature_columns, feature_display, target_col, platform_name):
    """Select by CV on training data then evaluate the selected model once."""
    X = df[feature_columns].copy()
    y = df[target_col].astype(int).copy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

    # Kept for artifact/API compatibility. Tree models below use the raw schema.
    scaler = StandardScaler().fit(X_train)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = {'accuracy': 'accuracy', 'precision': 'precision', 'recall': 'recall', 'f1_score': 'f1', 'auc_roc': 'roc_auc'}
    cv_results = {}
    best_name, best_cv_f1 = None, float('-inf')
    models = candidate_models()
    for name, model in models.items():
        scores = cross_validate(clone(model), X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
        cv_results[name] = {metric: round(float(scores[f'test_{metric}'].mean()), 4) for metric in scoring}
        if cv_results[name]['f1_score'] > best_cv_f1:
            best_name, best_cv_f1 = name, cv_results[name]['f1_score']

    # Report each candidate once on the held-out partition. These values are
    # never used for selection; ``best_name`` above was chosen from CV only.
    held_out_results = {}
    model = None
    for name, candidate in models.items():
        fitted = clone(candidate).fit(X_train, y_train)
        positive_index = list(fitted.classes_).index(1)
        held_out_results[name] = metrics_from_predictions(y_test, fitted.predict(X_test), fitted.predict_proba(X_test)[:, positive_index])
        if name == best_name:
            model = fitted
    result = held_out_results[best_name]
    majority_class = int(y_train.mode().iat[0])
    baseline = {'model_name': 'Majority class baseline', 'predicted_class': majority_class, **metrics_from_predictions(y_test, np.full(len(y_test), majority_class), np.full(len(y_test), float(y_train.mean())))}
    quality = {'status': 'deployable', 'reason': None}
    if result['accuracy'] <= baseline['accuracy'] or result['auc_roc'] < 0.55:
        quality = {'status': 'not_deployable', 'reason': 'Held-out performance does not beat the majority baseline with useful ROC-AUC; obtain a labelled feature-complete Twitter dataset before relying on predictions.'}

    importance = {}
    if hasattr(model, 'feature_importances_'):
        importance = dict(sorted(((display, round(float(value), 4)) for display, value in zip(feature_display, model.feature_importances_)), key=lambda item: item[1], reverse=True))
    metadata = {
        'platform': platform_name, 'best_model': best_name, 'feature_columns': feature_columns, 'feature_names_display': feature_display,
        'results': held_out_results, 'cross_validation_results': cv_results, 'majority_baseline': baseline,
        'evaluation': {'selection_split': '5-fold stratified CV on training data', 'test_split': '20% stratified held-out test data', 'positive_class': 1, 'positive_class_name': 'bot/fake'},
        'quality': quality, 'feature_importance': importance, 'needs_scaling': False,
        'training_samples': len(X_train), 'test_samples': len(X_test), 'total_samples': len(df),
    }
    return model, scaler, metadata


def save_model(model, scaler, metadata, model_dir, platform_name):
    os.makedirs(model_dir, exist_ok=True)
    for suffix, value in [('model.pkl', model), ('scaler.pkl', scaler)]:
        with open(os.path.join(model_dir, f'{platform_name}_{suffix}'), 'wb') as handle:
            pickle.dump(value, handle)
    with open(os.path.join(model_dir, f'{platform_name}_metadata.json'), 'w', encoding='utf-8') as handle:
        json.dump(metadata, handle, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform', choices=['instagram', 'twitter', 'all'], default='all')
    args = parser.parse_args()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    model_dir = os.path.join(root, 'backend', 'models')
    jobs = []
    if args.platform in ('instagram', 'all'):
        jobs.append(('insta', load_instagram_data(root), INSTA_FEATURE_COLUMNS, INSTA_FEATURE_DISPLAY, 'instagram'))
    if args.platform in ('twitter', 'all'):
        jobs.append(('twitter', load_twitter_data(root), TWITTER_FEATURE_COLUMNS, TWITTER_FEATURE_DISPLAY, 'twitter'))
    for artifact_name, frame, columns, display, platform in jobs:
        if frame is None:
            raise FileNotFoundError(f'No {platform} training data found')
        model, scaler, metadata = train_platform_model(frame, columns, display, 'is_fake', platform)
        save_model(model, scaler, metadata, model_dir, artifact_name)
        print(f"{platform}: {metadata['best_model']} held-out F1={metadata['results'][metadata['best_model']]['f1_score']:.4f}; quality={metadata['quality']['status']}")


if __name__ == '__main__':
    main()
