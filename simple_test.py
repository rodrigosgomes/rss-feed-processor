#!/usr/bin/env python3
"""
Simple Production Test - Teste Simples para Produção
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🚀 RSS FEED PROCESSOR - SIMPLE PRODUCTION TEST")
    print("=" * 60)
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_good = True
    
    print("\n📋 1. CONFIGURATION CHECK")
    try:
        from config.settings import EMAIL_SETTINGS, read_file_lines
        
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'feeds.txt')
        feed_urls = read_file_lines(config_path)
        print(f"   📄 Feed URLs: {len(feed_urls)} configured")
        print(f"   📧 Email Settings: {'✅ Configured' if EMAIL_SETTINGS else '❌ Missing'}")
        
        if not EMAIL_SETTINGS:
            all_good = False
            
    except Exception as e:
        print(f"   ❌ Configuration failed: {str(e)}")
        all_good = False
    
    print("\n📡 2. RSS READER CHECK")    try:
        from agents.rss_reader import RssReader
        
        # Load feed URLs for the reader
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'feeds.txt')
        feed_urls = read_file_lines(config_path)
        
        reader = RssReader(feed_urls[:3])  # Test with first 3 feeds
        print("   ✅ RSS Reader initialized")
        
        # Quick test reading feeds
        news_items = reader.read_feeds()
        print(f"   📰 Found {len(news_items)} recent articles")
        
        if len(news_items) == 0:
            print("   ⚠️  No recent articles found")
            
    except Exception as e:
        print(f"   ❌ RSS Reader failed: {str(e)}")
        all_good = False
        news_items = []
    
    print("\n🤖 3. SUMMARIZER CHECK")
    try:
        from agents.summarizer import Summarizer
        summarizer = Summarizer()
        print("   ✅ Summarizer initialized")
        
        if news_items and len(news_items) > 0:
            # Test with just one article
            test_items = news_items[:1]
            summary = summarizer.summarize(test_items, days=7)
            
            if summary:
                print("   ✅ Summary generation working")
            else:
                print("   ❌ Summary generation failed")
                all_good = False
        else:
            print("   ⚠️  No articles to test summarization")
            
    except Exception as e:
        print(f"   ❌ Summarizer failed: {str(e)}")
        all_good = False
    
    print("\n📧 4. EMAIL SYSTEM CHECK")
    try:
        if EMAIL_SETTINGS:
            from utils.email_sender import EmailSender
            email_sender = EmailSender(EMAIL_SETTINGS)
            print("   ✅ Email sender initialized")
            print(f"   📬 SMTP server: {EMAIL_SETTINGS.get('smtp_server')}")
            print(f"   👤 Sender: {EMAIL_SETTINGS.get('sender_email')}")
        else:
            print("   ❌ Email settings not configured")
            all_good = False
            
    except Exception as e:
        print(f"   ❌ Email system failed: {str(e)}")
        all_good = False
    
    print("\n🎯 5. PRODUCTION READINESS")
    if all_good:
        print("   ✅ SYSTEM STATUS: READY FOR PRODUCTION")
        print("   🚀 All components working correctly")
        print("   📋 Ready for automated deployment")
        return 0
    else:
        print("   ❌ SYSTEM STATUS: NEEDS ATTENTION") 
        print("   🔧 Review failed components above")
        print("   📋 Fix issues before production deployment")
        return 1

if __name__ == "__main__":
    sys.exit(main())
