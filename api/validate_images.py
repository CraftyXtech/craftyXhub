"""
Validate Unsplash image URLs from seed_full_posts.py
Run: python3 validate_images.py
"""
import urllib.request
import urllib.error
import re
import concurrent.futures

# All image URLs from seed_full_posts.py (UPDATED)
URLS_TO_TEST = {
    # Artificial Intelligence
    "artificial-intelligence-1": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80",
    "artificial-intelligence-2": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80",
    "artificial-intelligence-3": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&q=80",
    
    # Blockchain
    "blockchain-1": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&q=80",
    "blockchain-2": "https://images.unsplash.com/photo-1642104704074-907c0698cbd9?w=800&q=80",
    "blockchain-3": "https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800&q=80",
    
    # Automation
    "automation-1": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
    "automation-2": "https://images.unsplash.com/photo-1557200134-90327ee9fafa?w=800&q=80",
    "automation-3": "https://images.unsplash.com/photo-1556155092-490a1ba16284?w=800&q=80",
    
    # Programming
    "programming-1": "https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=800&q=80",
    "programming-2": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=800&q=80",
    "programming-3": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=800&q=80",
    
    # Cybersecurity
    "cybersecurity-1": "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80",
    "cybersecurity-2": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80",
    "cybersecurity-3": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80",
    
    # Entrepreneurship
    "entrepreneurship-1": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&q=80",
    "entrepreneurship-2": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
    "entrepreneurship-3": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80",
    
    # Personal Finance
    "finance-1": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "finance-2": "https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=800&q=80",
    "finance-3": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800&q=80",
    
    # Creator Economy
    "creator-1": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
    "creator-2": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&q=80",
    "creator-3": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=800&q=80",
    
    # Online Business
    "business-1": "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a?w=800&q=80",
    "business-2": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&q=80",
    "business-3": "https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=800&q=80",
    
    # Passive Income
    "passive-1": "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=800&q=80",
    "passive-2": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80",
    "passive-3": "https://images.unsplash.com/photo-1595675024853-0f3ec9098ac7?w=800&q=80",
    
    # Career Development
    "career-1": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800&q=80",
    "career-2": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=800&q=80",
    "career-3": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800&q=80",
    
    # Online Learning
    "learning-1": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?w=800&q=80",
    "learning-2": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&q=80",
    "learning-3": "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80",
    
    # Productivity
    "productivity-1": "https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=800&q=80",
    "productivity-2": "https://images.unsplash.com/photo-1434626881859-194d67b2b86f?w=800&q=80",
    "productivity-3": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=800&q=80",
    
    # Remote Work
    "remote-1": "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800&q=80",
    "remote-2": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
    "remote-3": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&q=80",
    
    # Personal Branding
    "branding-1": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80",
    "branding-2": "https://images.unsplash.com/photo-1504805572947-34fad45aed93?w=800&q=80",
    "branding-3": "https://images.unsplash.com/photo-1552581234-26160f608093?w=800&q=80",
    
    # Mental Health
    "mental-1": "https://images.unsplash.com/photo-1493839523149-2864fca44919?w=800&q=80",
    "mental-2": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80",
    "mental-3": "https://images.unsplash.com/photo-1474418397713-7ede21d49118?w=800&q=80",
    
    # Personal Growth
    "growth-1": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80",
    "growth-2": "https://images.unsplash.com/photo-1517842645767-c639042777db?w=800&q=80",
    "growth-3": "https://images.unsplash.com/photo-1494178270175-e96de2971df9?w=800&q=80",
    
    # Minimalism
    "minimalism-1": "https://images.unsplash.com/photo-1493723843671-1d655e66ac1c?w=800&q=80",
    "minimalism-2": "https://images.unsplash.com/photo-1449247709967-d4461a6a6103?w=800&q=80",
    "minimalism-3": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
    
    # Wellness
    "wellness-1": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&q=80",
    "wellness-2": "https://images.unsplash.com/photo-1445510491599-c391e8046a68?w=800&q=80",
    "wellness-3": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&q=80",
    
    # Sustainable Living
    "sustainable-1": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&q=80",
    "sustainable-2": "https://images.unsplash.com/photo-1558171813-4c088753af8f?w=800&q=80",
    "sustainable-3": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&q=80",
}


def check_url(item: tuple) -> tuple:
    """Check if a URL is accessible"""
    key, url = item
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req, timeout=10) as response:
            return (key, url, response.status)
    except urllib.error.HTTPError as e:
        return (key, url, e.code)
    except Exception:
        return (key, url, 0)


def main():
    print("🔍 Validating Unsplash image URLs...\n")
    
    broken = []
    working = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_url, URLS_TO_TEST.items()))
    
    for key, url, status in results:
        photo_id = re.search(r'photo-([a-zA-Z0-9-]+)', url)
        photo_id = photo_id.group(1) if photo_id else "unknown"
        
        if status == 200:
            working.append((key, photo_id))
            print(f"  ✅ {key}: OK")
        else:
            broken.append((key, url, status))
            print(f"  ❌ {key}: HTTP {status} - photo-{photo_id}")
    
    print(f"\n{'='*60}")
    print(f"📊 Results: {len(working)} working, {len(broken)} broken")
    
    if broken:
        print(f"\n🔴 BROKEN URLs ({len(broken)}):")
        for key, url, status in broken:
            print(f"  - {key}: {url}")
    else:
        print("\n🎉 All URLs are valid!")


if __name__ == "__main__":
    main()
