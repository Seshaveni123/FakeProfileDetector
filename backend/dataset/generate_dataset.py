"""
Generate a synthetic dataset for fake profile detection.
This creates realistic-looking data with patterns that distinguish real vs fake accounts.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

def generate_dataset(n_samples=5000):
    """Generate synthetic social media profile dataset."""
    
    # Split: 60% real, 40% fake
    n_real = int(n_samples * 0.6)
    n_fake = n_samples - n_real
    
    data = []
    
    # ===================== REAL PROFILES =====================
    for _ in range(n_real):
        followers = int(np.random.lognormal(mean=5, sigma=2))
        followers = min(followers, 5_000_000)
        
        following = int(np.random.lognormal(mean=4.5, sigma=1.5))
        following = min(following, 10_000)
        
        # Real users have reasonable ratio
        ratio = followers / max(following, 1)
        
        account_age_days = int(np.random.uniform(180, 4000))
        
        bio_length = int(np.random.normal(80, 30))
        bio_length = max(0, min(bio_length, 160))
        
        has_profile_pic = np.random.choice([1, 0], p=[0.92, 0.08])
        
        # Activity
        posts_per_day = round(np.random.exponential(0.8), 2)
        posts_per_day = min(posts_per_day, 10)
        
        avg_likes = int(np.random.lognormal(mean=2.5, sigma=1.5))
        avg_likes = min(avg_likes, followers * 0.3)
        
        avg_comments = int(avg_likes * np.random.uniform(0.02, 0.15))
        
        hashtags_per_post = round(np.random.uniform(0, 8), 1)
        
        has_url = np.random.choice([1, 0], p=[0.35, 0.65])
        
        # Behavior
        posting_regularity = round(np.random.uniform(0.3, 0.95), 2)  # Higher = more regular/human
        
        content_repetition_score = round(np.random.uniform(0.0, 0.25), 2)  # Low repetition for real
        
        engagement_consistency = round(np.random.uniform(0.5, 0.95), 2)  # High consistency
        
        is_fake = 0
        
        data.append([
            followers, following, ratio, account_age_days, bio_length,
            has_profile_pic, posts_per_day, avg_likes, avg_comments,
            hashtags_per_post, has_url, posting_regularity,
            content_repetition_score, engagement_consistency, is_fake
        ])
    
    # ===================== FAKE PROFILES =====================
    for _ in range(n_fake):
        fake_type = np.random.choice(['bot', 'spam', 'engagement_farm', 'impersonator'], 
                                       p=[0.35, 0.30, 0.20, 0.15])
        
        if fake_type == 'bot':
            followers = int(np.random.uniform(0, 100))
            following = int(np.random.uniform(500, 7500))
            account_age_days = int(np.random.uniform(1, 120))
            bio_length = int(np.random.choice([0, np.random.randint(5, 20)]))
            has_profile_pic = np.random.choice([1, 0], p=[0.2, 0.8])
            posts_per_day = round(np.random.uniform(10, 50), 2)
            avg_likes = int(np.random.uniform(0, 3))
            hashtags_per_post = round(np.random.uniform(15, 30), 1)
            posting_regularity = round(np.random.uniform(0.85, 1.0), 2)  # Very regular = automated
            content_repetition_score = round(np.random.uniform(0.6, 1.0), 2)
            engagement_consistency = round(np.random.uniform(0.0, 0.2), 2)
            
        elif fake_type == 'spam':
            followers = int(np.random.uniform(50, 500))
            following = int(np.random.uniform(1000, 5000))
            account_age_days = int(np.random.uniform(10, 200))
            bio_length = int(np.random.uniform(100, 160))  # Spammy long bios
            has_profile_pic = np.random.choice([1, 0], p=[0.6, 0.4])
            posts_per_day = round(np.random.uniform(5, 30), 2)
            avg_likes = int(np.random.uniform(0, 10))
            hashtags_per_post = round(np.random.uniform(20, 30), 1)
            posting_regularity = round(np.random.uniform(0.7, 0.99), 2)
            content_repetition_score = round(np.random.uniform(0.5, 0.9), 2)
            engagement_consistency = round(np.random.uniform(0.05, 0.3), 2)
            
        elif fake_type == 'engagement_farm':
            followers = int(np.random.uniform(5000, 100000))
            following = int(np.random.uniform(5000, 100000))
            account_age_days = int(np.random.uniform(60, 500))
            bio_length = int(np.random.uniform(30, 100))
            has_profile_pic = 1
            posts_per_day = round(np.random.uniform(3, 15), 2)
            avg_likes = int(followers * np.random.uniform(0.001, 0.01))  # Very low engagement rate
            hashtags_per_post = round(np.random.uniform(10, 25), 1)
            posting_regularity = round(np.random.uniform(0.6, 0.95), 2)
            content_repetition_score = round(np.random.uniform(0.3, 0.7), 2)
            engagement_consistency = round(np.random.uniform(0.1, 0.4), 2)
            
        else:  # impersonator
            followers = int(np.random.uniform(100, 5000))
            following = int(np.random.uniform(50, 500))
            account_age_days = int(np.random.uniform(5, 90))
            bio_length = int(np.random.uniform(60, 160))
            has_profile_pic = 1
            posts_per_day = round(np.random.uniform(1, 5), 2)
            avg_likes = int(np.random.uniform(5, 100))
            hashtags_per_post = round(np.random.uniform(2, 10), 1)
            posting_regularity = round(np.random.uniform(0.3, 0.7), 2)
            content_repetition_score = round(np.random.uniform(0.4, 0.8), 2)
            engagement_consistency = round(np.random.uniform(0.2, 0.5), 2)
        
        ratio = followers / max(following, 1)
        avg_comments = int(avg_likes * np.random.uniform(0.0, 0.05))
        has_url = np.random.choice([1, 0], p=[0.55, 0.45])
        
        is_fake = 1
        
        data.append([
            followers, following, ratio, account_age_days, bio_length,
            has_profile_pic, posts_per_day, avg_likes, avg_comments,
            hashtags_per_post, has_url, posting_regularity,
            content_repetition_score, engagement_consistency, is_fake
        ])
    
    columns = [
        'followers_count', 'following_count', 'followers_following_ratio',
        'account_age_days', 'bio_length', 'has_profile_pic',
        'posts_per_day', 'avg_likes', 'avg_comments',
        'hashtags_per_post', 'has_url_in_bio', 'posting_regularity',
        'content_repetition_score', 'engagement_consistency', 'is_fake'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save dataset
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fake_profiles_dataset.csv')
    df.to_csv(dataset_path, index=False)
    
    print(f"✅ Dataset generated: {len(df)} samples")
    print(f"   Real: {len(df[df['is_fake']==0])}, Fake: {len(df[df['is_fake']==1])}")
    print(f"   Saved to: {dataset_path}")
    
    return df

if __name__ == "__main__":
    generate_dataset()
