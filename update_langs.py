import requests
import os

USERNAME = "t4lhaa"
TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

COLORS = {
    "C++": "#f34b7d",
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "CSS": "#663399",
    "HTML": "#e34c26",
    "C": "#555555",
    "Jupyter Notebook": "#DA5B0B",
    "Shell": "#89e051",
    "Java": "#b07219"
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
        width = (percent / 100) * 250
        color = COLORS.get(lang, "#858585")
        
        progress_bars += f'<rect mask="url(#rect-mask)" x="{current_x:.2f}" y="0" width="{width:.2f}" height="8" fill="{color}" />\n'
        current_x += width
        
        col = i // 3
        row = i % 3
        x_offset = col * 150
        y_offset = row * 25
        delay = 450 + (i * 150)
        
        legends += f'''
        <g transform="translate({x_offset}, {y_offset})">
          <g class="stagger" style="animation-delay: {delay}ms; opacity: 0; animation: fadeInAnimation 0.3s ease-in-out forwards;">
            <circle cx="5" cy="6" r="5" fill="{color}" />
            <text x="15" y="10" font-family="'Segoe UI', Ubuntu, Sans-Serif" font-size="11px" fill="#a9fef7">{lang} {percent:.1f}%</text>
          </g>
        </g>'''

    final_svg = f'''<svg width="300" height="165" viewBox="0 0 300 165" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    @keyframes fadeInAnimation {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @keyframes slideInAnimation {{ from {{ width: 0; }} to {{ width: 100%; }} }}
    #rect-mask rect {{ animation: slideInAnimation 1s ease-in-out forwards; }}
  </style>
  <rect x="0.5" y="0.5" rx="4.5" height="99%" width="299" fill="#0D1117" stroke="#e4e2e2" stroke-opacity="0.0" />
  <text x="25" y="35" font-family="'Segoe UI', Ubuntu, Sans-Serif" font-size="18px" font-weight="600" fill="#fe428e" style="animation: fadeInAnimation 0.8s ease-in-out forwards;">Most Used Languages</text>
  <g transform="translate(0, 55)">
    <svg x="25">
      <mask id="rect-mask"><rect x="0" y="0" width="250" height="8" fill="white" rx="5"/></mask>
      {progress_bars}
      <g transform="translate(0, 25)">
        {legends}
      </g>
    </svg>
  </g>
</svg>'''

    os.makedirs("assets", exist_ok=True)
    with open("assets/top-langs.svg", "w") as file:
        file.write(final_svg)

if __name__ == "__main__":
    build_svg()
