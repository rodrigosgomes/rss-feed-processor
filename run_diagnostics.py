#!/usr/bin/env python3
"""
RSS Feed Diagnostics Script
Run this to diagnose all RSS feeds and identify which ones are working
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from utils.feed_diagnostics import FeedDiagnostics
from config.settings import RSS_FEED_URLS
from utils.logger import logger
import json

def main():
    """Run comprehensive feed diagnostics"""
    print("🔍 RSS Feed Diagnostics Tool")
    print("=" * 50)
    
    # Initialize diagnostics
    diagnostics = FeedDiagnostics()
    
    # Get feed URLs from config
    feed_urls = RSS_FEED_URLS
    print(f"📊 Found {len(feed_urls)} feeds to diagnose")
    print()
    
    # Run diagnostics
    results = diagnostics.diagnose_all_feeds(feed_urls)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📈 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    summary = results['summary']
    print(f"Total feeds: {summary['total_feeds']}")
    print(f"Accessible feeds: {summary['accessible_feeds']}")
    print(f"Working feeds: {summary['working_feeds']}")
    print(f"Blocked feeds: {summary['blocked_feeds']}")
    print(f"Empty feeds: {summary['empty_feeds']}")
    print(f"Success rate: {summary['success_rate']}")
    
    print(f"\n📊 Feed Types:")
    for feed_type, count in summary['feed_types'].items():
        print(f"  {feed_type}: {count}")
    
    print(f"\n🔧 Working Parsing Strategies:")
    for strategy, count in summary['parsing_strategies'].items():
        print(f"  {strategy}: {count}")
    
    print(f"\n🌐 Working Header Variants:")
    for variant, count in summary['header_variants'].items():
        print(f"  Variant {variant}: {count}")
    
    # Show working feeds
    if summary['working_feed_urls']:
        print(f"\n✅ WORKING FEEDS ({len(summary['working_feed_urls'])}):")
        for url in summary['working_feed_urls']:
            print(f"  ✓ {url}")
    
    # Show blocked feeds
    if summary['blocked_feed_urls']:
        print(f"\n❌ BLOCKED FEEDS ({len(summary['blocked_feed_urls'])}):")
        for url in summary['blocked_feed_urls']:
            print(f"  ✗ {url}")
    
    # Show empty feeds
    if summary['empty_feed_urls']:
        print(f"\n⚠️ EMPTY FEEDS ({len(summary['empty_feed_urls'])}):")
        for url in summary['empty_feed_urls']:
            print(f"  ⚠ {url}")
    
    # Show detailed results for working feeds
    working_results = [r for r in results['individual_results'] if r['items_found'] > 0]
    if working_results:
        print(f"\n📋 DETAILED RESULTS FOR WORKING FEEDS:")
        print("-" * 50)
        for result in working_results:
            print(f"\n🔗 {result['url']}")
            print(f"   Items found: {result['items_found']}")
            print(f"   Feed type: {result['feed_type']}")
            print(f"   Parsing strategy: {result['parsing_strategy']}")
            print(f"   Working headers: Variant {result['working_headers']}")
            print(f"   Content type: {result['content_type']}")
            
            if result['sample_items']:
                print(f"   Sample item: {result['sample_items'][0].get('title', 'No title')[:60]}...")
            
            if result['date_formats']:
                print(f"   Date formats: {', '.join(result['date_formats'])}")
    
    # Save detailed results to file
    output_file = current_dir / "feed_diagnostics_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print(f"\n🎯 Next steps:")
    print("1. Review blocked feeds and consider alternative sources")
    print("2. Update RSS reader to use optimal header variants for each feed")
    print("3. Implement feed-specific parsing strategies")
    print("4. Test the complete system with working feeds")

if __name__ == "__main__":
    main()
