"""
Train ML models for fake profile detection.
Trains Logistic Regression, Random Forest, and XGBoost, then saves the best model.
"""

import pandas as pd
import numpy as np
import pickle
import json
import os
import sys

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)

# Try importing XGBoost (optional)
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("⚠️  XGBoost not installed. Skipping XGBoost model.")


FEATURE_COLUMNS = [
    'followers_count', 'following_count', 'followers_following_ratio',
    'account_age_days', 'bio_length', 'has_profile_pic',
    'posts_per_day', 'avg_likes', 'avg_comments',
    'hashtags_per_post', 'has_url_in_bio', 'posting_regularity',
    'content_repetition_score', 'engagement_consistency'
]

FEATURE_NAMES_DISPLAY = [
    'Followers Count', 'Following Count', 'Followers/Following Ratio',
    'Account Age (days)', 'Bio Length', 'Has Profile Picture',
    'Posts Per Day', 'Avg Likes', 'Avg Comments',
    'Hashtags Per Post', 'Has URL in Bio', 'Posting Regularity',
    'Content Repetition Score', 'Engagement Consistency'
]


def load_data():
    """Load the generated dataset."""
    dataset_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        '..', 'dataset', 'fake_profiles_dataset.csv'
    )
    df = pd.read_csv(dataset_path)
    print(f"📊 Loaded dataset: {df.shape[0]} samples, {df.shape[1]} features")
    return df


def train_and_evaluate():
    """Train multiple models, evaluate, and save the best one."""
    
    df = load_data()
    
    X = df[FEATURE_COLUMNS].values
    y = df['is_fake'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # ===================== MODELS =====================
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(
            n_estimators=200, max_depth=15, min_samples_split=5,
            min_samples_leaf=2, random_state=42, n_jobs=-1
        ),
    }
    
    if HAS_XGBOOST:
        models['XGBoost'] = XGBClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            random_state=42, use_label_encoder=False, eval_metric='logloss'
        )
    
    results = {}
    best_model = None
    best_score = 0
    best_name = ""
    
    print("\n" + "=" * 60)
    print("🤖 TRAINING MODELS")
    print("=" * 60)
    
    for name, model in models.items():
        print(f"\n🔄 Training {name}...")
        
        # Use scaled data for Logistic Regression, raw for tree-based
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]
        
        # Metrics
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
    
    print(f"\n🏆 Best Model: {best_name} (F1: {best_score:.4f})")
    
    # ===================== FEATURE IMPORTANCE =====================
    feature_importance = {}
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        for fname, imp in zip(FEATURE_NAMES_DISPLAY, importances):
            feature_importance[fname] = round(float(imp), 4)
        
        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        print("\n📊 Feature Importance (Top 5):")
        for i, (fname, imp) in enumerate(feature_importance.items()):
            if i >= 5:
                break
            print(f"   {i+1}. {fname}: {imp:.4f}")
    
    # ===================== SAVE =====================
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save model
    model_path = os.path.join(model_dir, 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(best_model, f)
    print(f"\n💾 Model saved to: {model_path}")
    
    # Save scaler
    scaler_path = os.path.join(model_dir, 'scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"💾 Scaler saved to: {scaler_path}")
    
    # Save metadata
    metadata = {
        'best_model': best_name,
        'feature_columns': FEATURE_COLUMNS,
        'feature_names_display': FEATURE_NAMES_DISPLAY,
        'results': results,
        'feature_importance': feature_importance,
        'needs_scaling': best_name == 'Logistic Regression',
        'training_samples': len(X_train),
        'test_samples': len(X_test)
    }
    
    metadata_path = os.path.join(model_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"💾 Metadata saved to: {metadata_path}")
    
    print("\n✅ Training complete!")
    return best_model, scaler, metadata


if __name__ == "__main__":
    train_and_evaluate()
