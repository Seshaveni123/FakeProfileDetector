"""
Train separate ML models for Instagram and Twitter fake profile detection.
Uses REAL datasets from instagram1/, instagram2/, twitter1/, twitter2/ directories.
Algorithms: Random Forest (primary) + XGBoost (optional).
Saves: insta_model.pkl, twitter_model.pkl, scalers, and metadata.
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
import sys

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("⚠️  XGBoost not installed. Using Random Forest only.")


# ===================== FEATURE DEFINITIONS =====================

# Instagram features (from instagram1 + instagram2 real datasets)
INSTA_FEATURE_COLUMNS = [
    'profile pic', 'nums/length username', 'fullname words',
    'nums/length fullname', 'name==username', 'description length',
    'external URL', 'private', '#posts', '#followers', '#follows'
]

INSTA_FEATURE_DISPLAY = [
    'Profile Pic', 'Nums in Username', 'Fullname Words',
    'Nums in Fullname', 'Name == Username', 'Description Length',
    'External URL', 'Private Account', 'Posts Count', 'Followers', 'Following'
]

# Twitter features (from twitter1 real dataset)  
TWITTER_FEATURE_COLUMNS = [
    'Retweet Count', 'Mention Count', 'Follower Count', 'Verified'
]

TWITTER_FEATURE_DISPLAY = [
    'Retweet Count', 'Mention Count', 'Follower Count', 'Verified'
]


def load_instagram_data(base_dir):
    """Load and merge Instagram datasets from instagram1/ and instagram2/ directories."""
    print("\n📂 Loading Instagram datasets...")

    dfs = []

    # Load instagram1/Instagram_fake_profile_dataset.csv
    path1 = os.path.join(base_dir, 'instagram1', 'Instagram_fake_profile_dataset.csv')
    if os.path.exists(path1):
        df1 = pd.read_csv(path1)
        print(f"   ✅ instagram1: {len(df1)} rows")
        dfs.append(df1)
    else:
        print(f"   ❌ Not found: {path1}")

    # Load instagram2/train.csv and instagram2/test.csv
    path2_train = os.path.join(base_dir, 'instagram2', 'train.csv')
    path2_test = os.path.join(base_dir, 'instagram2', 'test.csv')

    if os.path.exists(path2_train):
        df2 = pd.read_csv(path2_train)
        print(f"   ✅ instagram2/train: {len(df2)} rows")
        dfs.append(df2)

    if os.path.exists(path2_test):
        df3 = pd.read_csv(path2_test)
        print(f"   ✅ instagram2/test: {len(df3)} rows")
        dfs.append(df3)

    if not dfs:
        print("   ❌ No Instagram datasets found!")
        return None

    # Merge all Instagram data
    combined = pd.concat(dfs, ignore_index=True)

    # Rename 'fake' column to 'is_fake' for consistency
    if 'fake' in combined.columns:
        combined = combined.rename(columns={'fake': 'is_fake'})

    # Drop duplicates
    combined = combined.drop_duplicates()

    # Compute engineered features
    combined['follower_ratio'] = combined['#followers'] / combined['#follows'].replace(0, 1)

    print(f"\n📊 Instagram combined: {len(combined)} samples")
    print(f"   Real: {len(combined[combined['is_fake']==0])} | Fake: {len(combined[combined['is_fake']==1])}")

    return combined


def load_twitter_data(base_dir):
    """Load Twitter dataset from twitter1/ directory.
    
    twitter1/bot_detection_data.csv has columns:
    User ID, Username, Tweet, Retweet Count, Mention Count, 
    Follower Count, Verified, Bot Label, Location, Created At, Hashtags
    """
    print("\n📂 Loading Twitter datasets...")

    # Load twitter1 (main dataset with features)
    path1 = os.path.join(base_dir, 'twitter1', 'bot_detection_data.csv')
    if not os.path.exists(path1):
        print(f"   ❌ Not found: {path1}")
        return None

    df = pd.read_csv(path1)
    print(f"   ✅ twitter1: {len(df)} rows")

    # Rename Bot Label to is_fake
    if 'Bot Label' in df.columns:
        df = df.rename(columns={'Bot Label': 'is_fake'})

    # Convert Verified column: True/False → 1/0
    if 'Verified' in df.columns:
        df['Verified'] = df['Verified'].map({True: 1, False: 0, 'True': 1, 'False': 0}).fillna(0).astype(int)

    # Load twitter2 for additional bot labels (just id + account_type)
    path2 = os.path.join(base_dir, 'twitter2', 'twitter_human_bots_dataset.csv')
    if os.path.exists(path2):
        df2 = pd.read_csv(path2)
        bot_count = len(df2[df2['account_type'] == 'bot'])
        human_count = len(df2[df2['account_type'] == 'human'])
        print(f"   ✅ twitter2: {len(df2)} rows (bot={bot_count}, human={human_count})")
        print(f"   ℹ️  twitter2 has only id+type, used twitter1 for features")

    # Drop rows with missing values in feature columns
    df = df.dropna(subset=TWITTER_FEATURE_COLUMNS + ['is_fake'])

    # Drop duplicates
    df = df.drop_duplicates()

    print(f"\n📊 Twitter dataset: {len(df)} samples")
    print(f"   Real: {len(df[df['is_fake']==0])} | Bot/Fake: {len(df[df['is_fake']==1])}")

    return df


def train_platform_model(df, feature_columns, feature_display, target_col, platform_name):
    """Train models for a specific platform and return best model + metadata."""
    print(f"\n{'='*60}")
    print(f"🚀 TRAINING {platform_name.upper()} MODEL")
    print(f"{'='*60}")

    X = df[feature_columns].values
    y = df[target_col].values

    # Train/test split (80/20, stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"📊 Dataset: {len(df)} total | {len(X_train)} train | {len(X_test)} test")
    print(f"📊 Features: {len(feature_columns)}")
    print(f"📊 Features list: {feature_columns}")

    # ===================== DEFINE MODELS =====================
    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        ),
    }

    if HAS_XGBOOST:
        models['XGBoost'] = XGBClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            random_state=42, eval_metric='logloss'
        )

    results = {}
    best_model = None
    best_score = 0
    best_name = ""

    # ===================== TRAIN & EVALUATE =====================
    for name, model in models.items():
        print(f"\n🔄 Training {name}...")

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            'accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4),
            'auc_roc': round(auc, 4),
            'confusion_matrix': cm.tolist()
        }

        print(f"   ✅ Accuracy:  {acc:.4f}")
        print(f"   📊 Precision: {prec:.4f}")
        print(f"   🔍 Recall:    {rec:.4f}")
        print(f"   ⚡ F1 Score:  {f1:.4f}")
        print(f"   📈 AUC-ROC:   {auc:.4f}")

        if f1 > best_score:
            best_score = f1
            best_model = model
            best_name = name

    print(f"\n🏆 Best Model for {platform_name}: {best_name} (F1: {best_score:.4f})")

    # ===================== FEATURE IMPORTANCE =====================
    feature_importance = {}
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        for fname, imp in zip(feature_display, importances):
            feature_importance[fname] = round(float(imp), 4)

        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )

        print(f"\n📊 Top 5 Features for {platform_name}:")
        for i, (fname, imp) in enumerate(feature_importance.items()):
            if i >= 5:
                break
            bar = '█' * int(imp * 50)
            print(f"   {i+1}. {fname}: {imp:.4f}  {bar}")

    # ===================== BUILD METADATA =====================
    metadata = {
        'platform': platform_name,
        'best_model': best_name,
        'feature_columns': feature_columns,
        'feature_names_display': feature_display,
        'results': results,
        'feature_importance': feature_importance,
        'needs_scaling': False,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'total_samples': len(df),
    }

    return best_model, scaler, metadata


def save_model(model, scaler, metadata, model_dir, platform_name):
    """Save model, scaler, and metadata to disk."""
    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(model_dir, f'{platform_name}_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"💾 Model saved:    {model_path}")

    scaler_path = os.path.join(model_dir, f'{platform_name}_scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"💾 Scaler saved:   {scaler_path}")

    meta_path = os.path.join(model_dir, f'{platform_name}_metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"💾 Metadata saved: {meta_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from ml/ to project root
    project_root = os.path.join(base_dir, '..')
    model_dir = os.path.join(project_root, 'models')

    # ===================== TRAIN INSTAGRAM MODEL =====================
    insta_df = load_instagram_data(project_root)
    if insta_df is not None:
        insta_model, insta_scaler, insta_meta = train_platform_model(
            insta_df, INSTA_FEATURE_COLUMNS, INSTA_FEATURE_DISPLAY,
            'is_fake', 'instagram'
        )
        save_model(insta_model, insta_scaler, insta_meta, model_dir, 'insta')
    else:
        print("❌ Skipping Instagram model — no data found")
        sys.exit(1)

    # ===================== TRAIN TWITTER MODEL =====================
    twitter_df = load_twitter_data(project_root)
    if twitter_df is not None:
        twitter_model, twitter_scaler, twitter_meta = train_platform_model(
            twitter_df, TWITTER_FEATURE_COLUMNS, TWITTER_FEATURE_DISPLAY,
            'is_fake', 'twitter'
        )
        save_model(twitter_model, twitter_scaler, twitter_meta, model_dir, 'twitter')
    else:
        print("❌ Skipping Twitter model — no data found")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("✅ ALL MODELS TRAINED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"📁 Models saved to: {os.path.abspath(model_dir)}")
    print(f"   - insta_model.pkl  ({insta_meta['best_model']})")
    print(f"   - twitter_model.pkl ({twitter_meta['best_model']})")
