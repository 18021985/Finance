"""
Test script for the Financial Analyzer
Tests the complete analysis pipeline with sample companies
"""

from analyzer import FinancialAnalyzer
import json

def test_single_company():
    """Test analysis of a single company"""
    print("=" * 60)
    print("Testing Single Company Analysis: AAPL")
    print("=" * 60)
    
    analyzer = FinancialAnalyzer()
    
    try:
        result = analyzer.analyze_company("AAPL", format="json")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"\n✅ Analysis successful for {result['symbol']}")
        print(f"\nCompany: {result['company'].get('name', 'N/A')}")
        print(f"Sector: {result['company'].get('sector', 'N/A')}")
        print(f"Current Price: ${result['company'].get('current_price', 0):.2f}")
        
        print(f"\n--- Scores ---")
        print(f"Bullish Score: {result['scores']['bullish_score']}")
        print(f"Bearish Score: {result['scores']['bearish_score']}")
        print(f"Net Score: {result['scores']['net_score']}")
        print(f"Signal Ratio: {result['scores']['signal_ratio']:.1%}")
        
        print(f"\n--- Verdict ---")
        print(f"Recommendation: {result['verdict']['verdict']}")
        print(f"Direction: {result['verdict']['direction']}")
        print(f"Probability: {result['verdict']['probability']:.0%}")
        
        print(f"\n--- Top 3 Bullish Signals ---")
        for i, signal in enumerate(result['bullish_indicators'][:3], 1):
            print(f"{i}. {signal['name']} ({signal['category']}) - Score: {signal['weighted_score']}")
        
        print(f"\n--- Top 3 Bearish Signals ---")
        for i, signal in enumerate(result['bearish_indicators'][:3], 1):
            print(f"{i}. {signal['name']} ({signal['category']}) - Score: {signal['weighted_score']}")
        
        print(f"\n--- Forecast ---")
        print(f"Short-Term: {result['forecast']['short_term']['direction']} ({result['forecast']['short_term']['probability']:.0%})")
        print(f"Long-Term: {result['forecast']['long_term']['direction']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_market_overview():
    """Test market overview"""
    print("\n" + "=" * 60)
    print("Testing Market Overview")
    print("=" * 60)
    
    analyzer = FinancialAnalyzer()
    
    try:
        overview = analyzer.get_market_overview()
        
        if 'error' in overview:
            print(f"❌ Error: {overview['error']}")
            return False
        
        print("\n✅ Market overview successful")
        print("\n--- Market Indices ---")
        for name, value in overview.get('indices', {}).items():
            print(f"{name}: {value}")
        
        print("\n--- Macro Indicators ---")
        for name, data in overview.get('macro_indicators', {}).items():
            print(f"{name}: {data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def test_scan_opportunities():
    """Test scanning multiple companies"""
    print("\n" + "=" * 60)
    print("Testing Opportunity Scan")
    print("=" * 60)
    
    analyzer = FinancialAnalyzer()
    
    try:
        symbols = ["AAPL", "MSFT", "GOOGL"]
        print(f"\nScanning: {', '.join(symbols)}")
        
        results = analyzer.scan_opportunities(symbols)
        
        print(f"\n✅ Scan complete - Analyzed {results['total_analyzed']} companies")
        print("\n--- Opportunities (Ranked by Net Score) ---")
        for i, opp in enumerate(results['opportunities'], 1):
            print(f"{i}. {opp['symbol']} ({opp['company']})")
            print(f"   Verdict: {opp['verdict']} | Net Score: {opp['net_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_markdown_output():
    """Test markdown output format"""
    print("\n" + "=" * 60)
    print("Testing Markdown Output Format")
    print("=" * 60)
    
    analyzer = FinancialAnalyzer()
    
    try:
        result = analyzer.analyze_company("AAPL", format="markdown")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print("\n✅ Markdown output successful")
        print("\n--- Markdown Output ---")
        print(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FINANCIAL ANALYZER TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Single Company Analysis", test_single_company()))
    results.append(("Market Overview", test_market_overview()))
    results.append(("Opportunity Scan", test_scan_opportunities()))
    results.append(("Markdown Output", test_markdown_output()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {len(results) - total_passed} test(s) failed")
