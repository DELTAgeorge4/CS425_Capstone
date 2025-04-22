import vt
import time

# Read the API key from the file
with open("/home/API_KEY/api_key.txt", "r") as f:
    API_KEY = f.read().strip()

# Create the client
with vt.Client(API_KEY) as client:
    # Open the file you want to scan
    with open("/home/API_KEY/api_key.txt", "rb") as f:
        analysis = client.scan_file(f)
        
    # Print the analysis ID
    print(f"Analysis ID: {analysis.id}")
    
    # Wait for analysis to complete
    # You might want to add a timeout or implement polling
    analysis_id = analysis.id
    try:
        # Wait for the analysis to complete
        analysis = client.wait_for_analysis_completion(analysis_id, timeout=60)  # 60 seconds timeout
        
        # Get and print the analysis results
        results = client.get_object("/analyses/{}", analysis_id)
        print("\nScan Results:")
        print(f"Status: {results.status}")
        
        # Print detection stats
        stats = results.stats
        print(f"Malicious: {stats.get('malicious', 0)}")
        print(f"Suspicious: {stats.get('suspicious', 0)}")
        print(f"Undetected: {stats.get('undetected', 0)}")
        
        # Print individual engine results
        print("\nDetailed Results:")
        for engine_name, result in results.results.items():
            category = result.get('category', 'N/A')
            if category in ['malicious', 'suspicious']:
                print(f"{engine_name}: {category} - {result.get('result', 'N/A')}")
                
    except vt.APIError as e:
        print(f"Error getting results: {e}")