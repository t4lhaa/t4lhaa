import requests
import os

USERNAME = "t4lhaa"
TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

# Adjusted colors for a more vibrant, neon look against the dark theme
COLORS = {
    "C++": "#ff4ea0",
    "Python": "#4584b6",
    "JavaScript": "#f7df1e",
    "CSS": "#7952b3",
    "HTML": "#e34c26",
    "C": "#a8b9cc",
    "Jupyter Notebook": "#ff8a00",
    "Shell": "#89e051",
    "Java": "#ea2d2e"
}

def fetch_language_data():
    repos_response = requests.get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100", headers=HEADERS)
    if repos_response.status_code != 200:
        return {}

    lang_stats = {}
    for repo in repos_response.json():
        if repo.get("fork"): 
            continue
            
        lang_url = repo['languages_url']
        lang_data = requests.get(lang_url, headers=HEADERS).json()
        
        if isinstance(lang_data, dict):
            for lang, bytes_count in lang_data.items():
                lang_stats[lang] = lang_stats.get(lang, 0) + bytes_count
    return lang_stats

def build_svg():
    lang_stats = fetch_language_data()
    if not lang_stats:
        return

    top_langs = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    total_bytes = sum(count for _, count in top_langs)

    progress_bars = ""
    legends = ""
    current_x = 0.0

    for i, (lang, bytes_count) in enumerate(top_langs):
        percent = (bytes_count / total_bytes) * 100
        # 260px is the total width of the new bar
        width = (percent / 100) * 260 
        color = COLORS.get(lang, "#858585")
        
        # We add rounded edges and a drop shadow filter to the bars
        progress_bars += f'<rect x="{current_x:.2f}" y="0" width="{width:.2f}" height="10" fill="{color}" filter="url(#glow)" />\n'
        current_x += width
        
        # Calculate grid position for legends
        col = i // 3
        row = i % 3
        x_offset = col * 135
        y_offset = row * 28
        delay = 450 + (i * 150)
        
        legends += f'''
        <g transform="translate({x_offset}, {y_offset})">
          <g style="animation: fadeIn 0.5s ease-in-out {delay}ms forwards; opacity: 0;">
            <circle cx="5" cy="6" r="6" fill="{color}" />
            <text x="20" y="10" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="12px" font-weight="500" fill="#c9d1d9">{lang}</text>
            <text x="20" y="24" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="10px" font-weight="400" fill="#8b949e">{percent:.1f}%</text>
          </g>
        </g>'''

    # The upgraded SVG Template with gradients, filters, and animations
    final_svg = f'''<svg width="350" height="200" viewBox="0 0 350 200" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117" />
      <stop offset="100%" stop-color="#161b22" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#000000" flood-opacity="0.3"/>
    </filter>
  </defs>
  
  <style>
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes slideRight {{ from {{ stroke-dashoffset: 260; }} to {{ stroke-dashoffset: 0; }} }}
    .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 18px; font-weight: 700; fill: #ffffff; letter-spacing: 0.5px; animation: fadeIn 0.8s ease-out forwards; }}
    .bar-mask {{ stroke-dasharray: 260; stroke-dashoffset: 260; animation: slideRight 1.2s cubic-bezier(0.1, 0.5, 0.2, 1) forwards; }}
  </style>

  <rect x="5" y="5" rx="10" width="340" height="190" fill="url(#bg-gradient)" stroke="#30363d" stroke-width="1.5" filter="url(#shadow)" />
  
  <text x="30" y="40" class="title">Top Languages</text>
  
  <g transform="translate(30, 65)">
    <mask id="bar-reveal">
      <line x1="0" y1="5" x2="260" y2="5" stroke="white" stroke-width="12" stroke-linecap="round" class="bar-mask" />
    </mask>
    
    <rect x="0" y="0" width="260" height="10" rx="5" fill="#21262d" />
    
    <g mask="url(#bar-reveal)">
      {progress_bars}
    </g>
  </g>

  <g transform="translate(30, 95)">
    {legends}
  </g>
</svg>'''

    os.makedirs("assets", exist_ok=True)
    with open("assets/top-langs.svg", "w") as file:
        file.write(final_svg)

if __name__ == "__main__":
    build_svg()
