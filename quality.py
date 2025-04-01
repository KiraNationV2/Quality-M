import os
import time
import json
import requests
from datetime import datetime
from pyfiglet import Figlet
from halo import Halo
from simple_chalk import chalk
from tabulate import tabulate
from tqdm import tqdm
import textwrap
import unicodedata
import sys
import webbrowser
import zipfile
from random import choice

class Config:
    RESULTS_DIR = "Results"
    HTML_EXPORTS_DIR = "HTML_Exports"
    BACKUP_DIR = "Backups"
    MAX_HISTORY = 50
    API_TIMEOUT = 50
    EMOJIS = ["🔍", "🔎", "🕵️", "👁️", "📊", "📈", "📉", "🔐", "🔒", "🔓"]

class TerminalUI:
    def __init__(self):
        self.spinner = Halo(text_color='cyan', spinner='dots')
        self.fig = Figlet(font='slant')
        self.screen_width = self.get_terminal_size()
        self.colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']
        
    def get_terminal_size(self):
        try:
            import shutil
            return min(shutil.get_terminal_size().columns, 120)
        except:
            return 80

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        self.clear_screen()
        banner_text = "QUALITY-M"
        banner = ""
        for line in self.fig.renderText(banner_text).split('\n'):
            colored_line = ""
            for char in line:
                color = choice(self.colors)
                colored_line += getattr(chalk, color)(char)
            banner += colored_line + "\n"
        
        print(banner)
        print(getattr(chalk, 'blue').bold("═" * self.screen_width))
        print(getattr(chalk, 'yellow')("Versão Ultra Pro | " + datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        print(getattr(chalk, 'blue').bold("═" * self.screen_width))
        
    def show_menu(self):
        menu_options = [
            ["1", f"{choice(Config.EMOJIS)} Pesquisar Logins"],
            ["2", f"{choice(Config.EMOJIS)} Ver Histórico"],
            ["3", f"{choice(Config.EMOJIS)} Gerenciar Resultados"],
            ["4", f"{choice(Config.EMOJIS)} Exportar Dados"],
            ["5", f"{choice(Config.EMOJIS)} Ferramentas"],
            ["0", f"{choice(Config.EMOJIS)} Sair"]
        ]
        
        print(getattr(chalk, 'magenta').bold("\nMENU PRINCIPAL:\n"))
        print(tabulate(menu_options, headers=["", ""], tablefmt="fancy_grid"))
        return input(getattr(chalk, 'yellow')("\n➤ Selecione uma opção: "))

    def loading_animation(self, text="Processando"):
        spinner_frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        with Halo(text=text, spinner={'interval': 100, 'frames': spinner_frames}, text_color='cyan') as spinner:
            time.sleep(1.5)
            spinner.succeed()

    def progress_bar(self, iterations=100, desc="Progresso"):
        color = choice(['green', 'blue', 'magenta'])
        for _ in tqdm(range(iterations), desc=getattr(chalk, color).bold(desc), unit="%", ncols=75):
            time.sleep(0.01)

    def show_results_table(self, data):
        headers = [
            getattr(chalk, 'blue').bold("Nº"), 
            getattr(chalk, 'blue').bold("Usuário"), 
            getattr(chalk, 'blue').bold("Senha"),
            getattr(chalk, 'blue').bold("Status")
        ]
        
        table_data = []
        for idx, account in enumerate(data.get('users_accounts', []), 1):
            user = textwrap.shorten(account.get('username', 'N/A'), width=20, placeholder="...")
            pwd = textwrap.shorten(account.get('password', 'N/A'), width=20, placeholder="...")
            status = self.generate_random_status()
            table_data.append([
                getattr(chalk, 'white')(idx),
                getattr(chalk, 'white')(user),
                getattr(chalk, 'white')(pwd),
                status
            ])
            
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

    def generate_random_status(self):
        statuses = {
            "✅ Ativo": "green",
            "⚠️ Expirado": "yellow",
            "❌ Inválido": "red",
            "🔒 Bloqueado": "magenta",
            "🔑 Válido": "cyan"
        }
        status, color = choice(list(statuses.items()))
        return getattr(chalk, color).bold(status)

class FileManager:
    def __init__(self):
        self.ensure_directories_exist()
        
    def ensure_directories_exist(self):
        os.makedirs(Config.RESULTS_DIR, exist_ok=True)
        os.makedirs(Config.HTML_EXPORTS_DIR, exist_ok=True)
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)

    def save_results(self, url, data):
        filename = self.generate_filename(url, "txt", Config.RESULTS_DIR)
        filepath = os.path.join(Config.RESULTS_DIR, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.generate_file_header(url, data))
                f.write(self.generate_results_table(data))
                f.write(self.generate_file_footer(data))
            return filepath
        except Exception as e:
            print(getattr(chalk, 'red')(f"Erro ao salvar arquivo: {e}"))
            return None

    def generate_filename(self, base, ext, dir_type):
        base = base.replace('https://', '').replace('http://', '').replace('/', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rand_str = ''.join(choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(4))
        return f"{dir_type.lower()}_{base[:20]}_{timestamp}_{rand_str}.{ext}"

    def generate_file_header(self, url, data):
        header = []
        header.append("╔" + "═" * 88 + "╗")
        header.append("║" + f"🔍 RESULTADOS PARA: {url}".center(88) + "║")
        header.append("║" + f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}".center(88) + "║")
        header.append("╠" + "═" * 88 + "╣")
        return "\n".join(header) + "\n"

    def generate_results_table(self, data):
        table = []
        table.append("┌" + "─" * 24 + "┬" + "─" * 24 + "┬" + "─" * 36 + "┐")
        table.append("│" + "USUÁRIO".center(24) + "│" + "SENHA".center(24) + "│" + "STATUS".center(36) + "│")
        table.append("├" + "─" * 24 + "┼" + "─" * 24 + "┼" + "─" * 36 + "┤")
        
        for account in data.get('users_accounts', []):
            user = self.format_cell(account.get('username', 'N/A'), 23)
            pwd = self.format_cell(account.get('password', 'N/A'), 23)
            status = self.generate_random_status_file()
            table.append(f"│ {user} │ {pwd} │ {status.center(36)} │")
            
        table.append("└" + "─" * 24 + "┴" + "─" * 24 + "┴" + "─" * 36 + "┘")
        return "\n".join(table) + "\n"

    def generate_random_status_file(self):
        statuses = ["ATIVO", "EXPIRADO", "INVÁLIDO", "BLOQUEADO", "VÁLIDO"]
        return choice(statuses)

    def format_cell(self, text, width):
        text = str(text)
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        return textwrap.shorten(text, width=width, placeholder="...").ljust(width)

    def generate_file_footer(self, data):
        footer = []
        footer.append("╠" + "═" * 88 + "╣")
        footer.append("║" + f"🔢 Total de contas: {data.get('total_accounts', 0)}".ljust(88) + "║")
        footer.append("║" + f"⏱ Tempo de resposta: {data.get('time', 'N/A')}".ljust(88) + "║")
        footer.append("╚" + "═" * 88 + "╝")
        return "\n".join(footer)

    def list_files(self, dir_type):
        dir_path = getattr(Config, dir_type.upper())
        return [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

    def clear_all_results(self, dir_type):
        dir_path = getattr(Config, dir_type.upper())
        try:
            for filename in os.listdir(dir_path):
                filepath = os.path.join(dir_path, filename)
                os.remove(filepath)
            return True
        except Exception as e:
            print(getattr(chalk, 'red')(f"Erro ao limpar {dir_type}: {e}"))
            return False

    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(Config.BACKUP_DIR, backup_name)
        
        try:
            with zipfile.ZipFile(backup_path, 'w') as zipf:
                for folder in [Config.RESULTS_DIR, Config.HTML_EXPORTS_DIR]:
                    for root, _, files in os.walk(folder):
                        for file in files:
                            zipf.write(os.path.join(root, file), 
                                      os.path.relpath(os.path.join(root, file), 
                                      os.path.join(folder, '..')))
            return backup_path
        except Exception as e:
            print(getattr(chalk, 'red')(f"Erro ao criar backup: {e}"))
            return None

class DataExporter:
    @staticmethod
    def export_to_html(data, filename):
        try:
            html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Resultados Quality Midia</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css">
    <style>
        :root {{
            --primary-color: #4361ee;
            --secondary-color: #3a0ca3;
            --accent-color: #f72585;
            --light-color: #f8f9fa;
            --dark-color: #212529;
            --success-color: #4cc9f0;
            --warning-color: #f8961e;
            --danger-color: #ef233c;
            --text-color: #2b2d42;
            --bg-gradient: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
            --card-shadow: 0 10px 20px -5px rgba(0,0,0,0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Poppins', sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--light-color);
            min-height: 100vh;
            padding: 2rem;
            background-image: 
                radial-gradient(at 80% 0%, hsla(189, 100%, 56%, 0.1) 0px, transparent 50%),
                radial-gradient(at 0% 50%, hsla(355, 100%, 93%, 0.1) 0px, transparent 50%);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            animation: fadeIn 0.6s ease-out;
        }}
        
        header {{
            background: var(--bg-gradient);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2.5rem;
            box-shadow: var(--card-shadow);
            text-align: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease;
        }}
        
        header:hover {{
            transform: translateY(-3px);
        }}
        
        header::after {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--accent-color);
        }}
        
        h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 600;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        }}
        
        .info-card {{
            background-color: white;
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2.5rem;
            box-shadow: var(--card-shadow);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            transition: all 0.3s ease;
            border: 1px solid rgba(0,0,0,0.05);
        }}
        
        .info-card:hover {{
            box-shadow: 0 15px 30px -10px rgba(0,0,0,0.15);
            transform: translateY(-3px);
        }}
        
        .info-item {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem;
            border-radius: 8px;
            transition: background-color 0.2s ease;
        }}
        
        .info-item:hover {{
            background-color: rgba(67, 97, 238, 0.05);
        }}
        
        .info-label {{
            font-weight: 600;
            color: var(--secondary-color);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.95rem;
        }}
        
        .info-label i {{
            font-size: 1.25rem;
        }}
        
        .info-value {{
            font-weight: 500;
            color: var(--text-color);
            margin-left: auto;
        }}
        
        .table-container {{
            overflow-x: auto;
            border-radius: 16px;
            box-shadow: var(--card-shadow);
            margin: 2.5rem 0;
            background: white;
            animation: slideUp 0.5s ease-out;
        }}
        
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            min-width: 600px;
        }}
        
        thead {{
            background: var(--bg-gradient);
            color: white;
        }}
        
        th {{
            padding: 1.25rem 1.5rem;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
            position: sticky;
            top: 0;
        }}
        
        th:first-child {{
            border-top-left-radius: 16px;
        }}
        
        th:last-child {{
            border-top-right-radius: 16px;
        }}
        
        td {{
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            transition: background-color 0.2s ease;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tr:hover td {{
            background-color: rgba(67, 97, 238, 0.03);
        }}
        
        tr:nth-child(even) td {{
            background-color: rgba(0,0,0,0.01);
        }}
        
        tr:nth-child(even):hover td {{
            background-color: rgba(67, 97, 238, 0.03);
        }}
        
        .status {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.75rem;
            border-radius: 50px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        .status-active {{
            background-color: rgba(76, 201, 240, 0.1);
            color: var(--success-color);
        }}
        
        .status-expired {{
            background-color: rgba(248, 150, 30, 0.1);
            color: var(--warning-color);
        }}
        
        .status-invalid {{
            background-color: rgba(239, 35, 60, 0.1);
            color: var(--danger-color);
        }}
        
        .status::before {{
            content: '';
            display: block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
        
        .status-active::before {{
            background-color: var(--success-color);
        }}
        
        .status-expired::before {{
            background-color: var(--warning-color);
        }}
        
        .status-invalid::before {{
            background-color: var(--danger-color);
        }}
        
        footer {{
            margin-top: 3rem;
            text-align: center;
            color: #6c757d;
            padding: 2rem;
            animation: fadeIn 0.8s ease-out;
        }}
        
        .footer-text {{
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        
        .timestamp {{
            font-size: 0.8rem;
            color: #adb5bd;
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        /* Responsive adjustments */
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            h1 {{
                font-size: 1.8rem;
            }}
            
            .info-card {{
                grid-template-columns: 1fr;
                padding: 1.5rem;
            }}
            
            th, td {{
                padding: 1rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            header {{
                padding: 1.5rem 1rem;
            }}
            
            h1 {{
                font-size: 1.5rem;
                flex-direction: column;
                gap: 0.5rem;
            }}
            
            .info-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 0.25rem;
            }}
            
            .info-value {{
                margin-left: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="animate__animated animate__fadeInDown">
            <h1>
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                Relatório Quality Midia
            </h1>
        </header>
        
        <div class="info-card animate__animated animate__fadeIn animate__delay-1s">
            <div class="info-item">
                <span class="info-label">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 12a9 9 0 0 1-9 9 9 9 0 0 1-9-9 9 9 0 0 1 9-9 9 9 0 0 1 9 9z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                        <path d="M12 2v2"></path>
                        <path d="M12 20v2"></path>
                        <path d="m4.93 4.93 1.41 1.41"></path>
                        <path d="m17.66 17.66 1.41 1.41"></path>
                        <path d="M2 12h2"></path>
                        <path d="M20 12h2"></path>
                        <path d="m6.34 17.66-1.41 1.41"></path>
                        <path d="m19.07 4.93-1.41 1.41"></path>
                    </svg>
                    URL:
                </span>
                <span class="info-value">{data.get('url_searched', 'N/A')}</span>
            </div>
            <div class="info-item">
                <span class="info-label">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    Data:
                </span>
                <span class="info-value">{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</span>
            </div>
            <div class="info-item">
                <span class="info-label">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                    Contas:
                </span>
                <span class="info-value">{data.get('total_accounts', 0)}</span>
            </div>
            <div class="info-item">
                <span class="info-label">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    Tempo:
                </span>
                <span class="info-value">{data.get('time', 'N/A')}</span>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Usuário</th>
                        <th>Senha</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([
                        f"""<tr class="animate__animated animate__fadeIn animate__delay-{(idx % 10) * 0.1 + 1.5}s">
                            <td>{idx + 1}</td>
                            <td>{account.get('username', 'N/A')}</td>
                            <td>{account.get('password', 'N/A')}</td>
                            <td>
                                <span class="status status-{choice(['active', 'expired', 'invalid'])}">
                                    {choice(['Ativo', 'Expirado', 'Inválido'])}
                                </span>
                            </td>
                        </tr>"""
                        for idx, account in enumerate(data.get('users_accounts', []))
                    ])}
                </tbody>
            </table>
        </div>

        <footer>
            <p class="footer-text">Relatório gerado automaticamente pelo Quality Midia Search Ultra Pro</p>
            <p class="timestamp">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>
"""
            
            os.makedirs(Config.HTML_EXPORTS_DIR, exist_ok=True)
            filepath = os.path.join(Config.HTML_EXPORTS_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            return filepath
        except Exception as e:
            print(getattr(chalk, 'red')(f"Erro ao exportar para HTML: {e}"))
            return None

    @staticmethod
    def export_to_json(data, filename):
        try:
            os.makedirs(Config.HTML_EXPORTS_DIR, exist_ok=True)
            filepath = os.path.join(Config.HTML_EXPORTS_DIR, filename)
            
            enhanced_data = {
                "metadata": {
                    "url_searched": data.get('url_searched', ''),
                    "search_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "total_accounts": data.get('total_accounts', 0),
                    "response_time": data.get('time', 'N/A'),
                    "version": "Quality Midia Ultra Pro"
                },
                "accounts": [
                    {
                        "username": acc.get('username', 'N/A'),
                        "password": acc.get('password', 'N/A'),
                        "status": choice(["active", "expired", "blocked", "valid"]),
                        "last_checked": datetime.now().strftime('%Y-%m-%d')
                    }
                    for acc in data.get('users_accounts', [])
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(enhanced_data, f, indent=4, ensure_ascii=False)
            
            return filepath
        except Exception as e:
            print(getattr(chalk, 'red')(f"Erro ao exportar para JSON: {e}"))
            return None

class SearchEngine:
    def __init__(self):
        self.api_url = "https://qualitymidia.com/logs.php"
        self.api_key = "QualityMidiaServer"
        self.history = []
        self.ui = TerminalUI()
        self.file_manager = FileManager()
        self.data_exporter = DataExporter()

    def search(self, url):
     try:
        self.ui.spinner.start(text="Realizando pesquisa avançada")
        
        self.ui.progress_bar(30, "Verificando URL")
        
        response = requests.get(
            f'{self.api_url}?url={url}&key={self.api_key}',
            timeout=Config.API_TIMEOUT
        )
        
        self.ui.progress_bar(70, "Analisando resultados")
        
        response.raise_for_status()
        data = response.json()
        
        if not isinstance(data, dict) or not data.get('users_accounts'):
            self.ui.spinner.fail(getattr(chalk, 'red')("Nenhum resultado encontrado"))
            return None
            
        if len(self.history) >= Config.MAX_HISTORY:
            self.history.pop(0)
            
        self.history.append({
            'url': url,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': len(data['users_accounts']),
            'data': data
        })
        
        self.ui.spinner.succeed(getattr(chalk, 'green')("Pesquisa concluída com sucesso!"))
        return data
        
     except requests.RequestException as e:
        self.ui.spinner.fail(getattr(chalk, 'red')(f"Erro na requisição: {e}"))
        return None
     except json.JSONDecodeError:
        self.ui.spinner.fail(getattr(chalk, 'red')("Resposta inválida da API"))
        return None
     except Exception as e:
        self.ui.spinner.fail(getattr(chalk, 'red')(f"Erro inesperado: {e}"))
        return None
    def run_search_flow(self):
        self.ui.show_banner()
        url = input(getattr(chalk, 'yellow')("\n🌐 Digite a URL para pesquisa: ")).strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
            
        data = self.search(url)
        if not data:
            input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            return
            
        self.ui.show_banner()
        print(getattr(chalk, 'green').bold(f"\n🎉 {data['total_accounts']} contas encontradas!"))
        self.ui.show_results_table(data)
        
        self.ui.progress_bar(desc="Salvando resultados")
        saved_file = self.file_manager.save_results(url, data)
        
        if saved_file:
            print(getattr(chalk, 'green').bold(f"\n💾 Resultados salvos em: {saved_file}"))
        
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def show_history(self):
        self.ui.show_banner()
        
        if not self.history:
            print(getattr(chalk, 'yellow')("\n⚠ Nenhum histórico disponível"))
            input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            return
            
        headers = [
            getattr(chalk, 'blue').bold("#"), 
            getattr(chalk, 'blue').bold("Hora"), 
            getattr(chalk, 'blue').bold("URL"), 
            getattr(chalk, 'blue').bold("Contas"),
            getattr(chalk, 'blue').bold("Ações")
        ]
        
        table_data = []
        for idx, item in enumerate(reversed(self.history), 1):
            actions = [
                getattr(chalk, 'cyan')("👁️ Ver"),
                getattr(chalk, 'green')("📤 Exportar"),
                getattr(chalk, 'yellow')("♻ Revalidar")
            ]
            table_data.append([
                getattr(chalk, 'white')(idx),
                getattr(chalk, 'white')(item['date'][11:19]),
                getattr(chalk, 'white')(textwrap.shorten(item['url'], width=30, placeholder="...")),
                getattr(chalk, 'green')(item['results']),
                " | ".join(actions)
            ])
            
        print("\n" + tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
        
        try:
            choice = input(getattr(chalk, 'yellow')("\n➤ Selecione uma pesquisa para ações (#) ou Enter para voltar: "))
            if choice.isdigit() and 1 <= int(choice) <= len(self.history):
                selected = self.history[-int(choice)]
                self.history_actions(selected)
        except:
            pass

    def history_actions(self, item):
        while True:
            self.ui.show_banner()
            print(getattr(chalk, 'cyan').bold(f"\nAÇÕES PARA PESQUISA: {item['url']}\n"))
            
            options = [
                ["1", "👁️ Visualizar resultados"],
                ["2", "📤 Exportar para HTML"],
                ["3", "📝 Exportar para JSON"],
                ["4", "♻ Revalidar contas"],
                ["0", "🔙 Voltar"]
            ]
            
            print(tabulate(options, headers=["", ""], tablefmt="fancy_grid"))
            action = input(getattr(chalk, 'yellow')("\n➤ Selecione uma ação: "))
            
            if action == '1':
                self.ui.show_banner()
                print(getattr(chalk, 'green').bold(f"\n🔍 Resultados para: {item['url']}"))
                self.ui.show_results_table(item['data'])
                input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            elif action == '2':
                filename = self.file_manager.generate_filename(item['url'], "html", "HTML_EXPORTS")
                exported = self.data_exporter.export_to_html(item['data'], filename)
                if exported:
                    print(getattr(chalk, 'green').bold(f"\n✔ Exportado para HTML: {exported}"))
                    if input(getattr(chalk, 'yellow')("Abrir no navegador? (s/n): ")).lower() == 's':
                        webbrowser.open(exported)
                input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            elif action == '3':
                filename = self.file_manager.generate_filename(item['url'], "json", "HTML_EXPORTS")
                exported = self.data_exporter.export_to_json(item['data'], filename)
                if exported:
                    print(getattr(chalk, 'green').bold(f"\n✔ Exportado para JSON: {exported}"))
                input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            elif action == '0':
                break
            else:
                print(getattr(chalk, 'red')("\n⚠ Opção inválida!"))
                time.sleep(1)

    def manage_results(self):
        while True:
            self.ui.show_banner()
            options = [
                ["1", "📋 Listar resultados salvos"],
                ["2", "👁️ Visualizar arquivo"],
                ["3", "🗑️ Limpar resultados"],
                ["4", "💾 Criar backup"],
                ["5", "📤 Exportar em massa"],
                ["0", "🔙 Voltar"]
            ]
            
            print(tabulate(options, headers=["", ""], tablefmt="fancy_grid"))
            choice = input(getattr(chalk, 'yellow')("\n➤ Selecione uma opção: "))
            
            if choice == '1':
                self.list_saved_results()
            elif choice == '2':
                self.view_specific_file()
            elif choice == '3':
                self.clear_results_menu()
            elif choice == '4':
                self.create_backup()
            elif choice == '5':
                self.bulk_export()
            elif choice == '0':
                break
            else:
                print(getattr(chalk, 'red')("\n⚠ Opção inválida!"))
                time.sleep(1)

    def list_saved_results(self):
        files = self.file_manager.list_files("RESULTS")
        if not files:
            print(getattr(chalk, 'yellow')("\n⚠ Nenhum resultado salvo encontrado"))
            input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            return
            
        headers = [
            getattr(chalk, 'blue').bold("#"), 
            getattr(chalk, 'blue').bold("Arquivo"), 
            getattr(chalk, 'blue').bold("Tamanho"), 
            getattr(chalk, 'blue').bold("Data")
        ]
        table_data = []
        
        for i, filename in enumerate(files, 1):
            filepath = os.path.join(Config.RESULTS_DIR, filename)
            size = os.path.getsize(filepath) / 1024
            date = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%d/%m %H:%M')
            table_data.append([
                getattr(chalk, 'white')(i),
                getattr(chalk, 'white')(textwrap.shorten(filename, width=30, placeholder="...")),
                getattr(chalk, 'white')(f"{size:.1f} KB"),
                getattr(chalk, 'white')(date)
            ])
            
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def view_specific_file(self):
        files = self.file_manager.list_files("RESULTS")
        if not files:
            print(getattr(chalk, 'yellow')("\n⚠ Nenhum resultado salvo encontrado"))
            input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            return

        self.ui.show_banner()
        print(getattr(chalk, 'cyan').bold("\nARQUIVOS DISPONÍVEIS:\n"))
        
        for i, filename in enumerate(files, 1):
            print(getattr(chalk, 'white')(f"{i}. {filename}"))
            
        try:
            choice = input(getattr(chalk, 'yellow')("\n➤ Selecione o arquivo (#) ou Enter para voltar: "))
            if choice.isdigit() and 1 <= int(choice) <= len(files):
                filepath = os.path.join(Config.RESULTS_DIR, files[int(choice)-1])
                self.display_file_content(filepath)
        except:
            pass

    def display_file_content(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.ui.show_banner()
            print(getattr(chalk, 'green').bold(f"\n📂 Conteúdo do arquivo: {os.path.basename(filepath)}\n"))
            print(getattr(chalk, 'white')(content))
            
        except Exception as e:
            print(getattr(chalk, 'red')(f"\n⚠ Erro ao ler arquivo: {e}"))
        
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def clear_results_menu(self):
        self.ui.show_banner()
        options = [
            ["1", "🧹 Limpar resultados de pesquisa"],
            ["2", "🗑️ Limpar exportações HTML"],
            ["3", "🔥 Limpar TUDO"],
            ["0", "🔙 Voltar"]
        ]
        
        print(tabulate(options, headers=["", ""], tablefmt="fancy_grid"))
        choice = input(getattr(chalk, 'yellow')("\n➤ Selecione o que deseja limpar: "))
        
        if choice == '1':
            self.clear_results("RESULTS")
        elif choice == '2':
            self.clear_results("HTML_EXPORTS")
        elif choice == '3':
            self.clear_results("ALL")
        elif choice != '0':
            print(getattr(chalk, 'red')("\n⚠ Opção inválida!"))
            time.sleep(1)

    def clear_results(self, dir_type):
        confirm = input(getattr(chalk, 'red')(f"\n⚠ Tem certeza que deseja apagar TODOS os arquivos {dir_type}? (s/n): "))
        if confirm.lower() != 's':
            print(getattr(chalk, 'yellow')("\nOperação cancelada"))
            return
            
        self.ui.loading_animation(f"Limpando {dir_type}")
        
        if dir_type == "ALL":
            success1 = self.file_manager.clear_all_results("RESULTS")
            success2 = self.file_manager.clear_all_results("HTML_EXPORTS")
            success = success1 and success2
        else:
            success = self.file_manager.clear_all_results(dir_type)
        
        if success:
            print(getattr(chalk, 'green')("\n✔ Limpeza concluída com sucesso!"))
        else:
            print(getattr(chalk, 'red')("\n✖ Erro durante a limpeza"))
            
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def create_backup(self):
        self.ui.loading_animation("Preparando backup")
        backup_path = self.file_manager.create_backup()
        
        if backup_path:
            size = os.path.getsize(backup_path) / (1024 * 1024)
            print(getattr(chalk, 'green').bold(f"\n✔ Backup criado com sucesso!"))
            print(getattr(chalk, 'white')(f"📍 Local: {backup_path}"))
            print(getattr(chalk, 'white')(f"📦 Tamanho: {size:.2f} MB"))
        else:
            print(getattr(chalk, 'red')("\n✖ Falha ao criar backup"))
            
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def bulk_export(self):
        if not self.history:
            print(getattr(chalk, 'yellow')("\n⚠ Nenhuma pesquisa no histórico para exportar"))
            input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            return
            
        self.ui.show_banner()
        print(getattr(chalk, 'cyan').bold("\nEXPORTAÇÃO EM MASSA\n"))
        
        formats = [
            ["1", "HTML (para visualização)"],
            ["2", "JSON (para análise)"],
            ["0", "Cancelar"]
        ]
        
        print(tabulate(formats, headers=["", ""], tablefmt="fancy_grid"))
        fmt = input(getattr(chalk, 'yellow')("\n➤ Selecione o formato de exportação: "))
        
        if fmt not in ['1', '2']:
            return
            
        ext = "html" if fmt == '1' else "json"
        
        self.ui.progress_bar(desc="Exportando dados")
        
        exported_files = []
        for item in self.history:
            filename = self.file_manager.generate_filename(item['url'], ext, "HTML_EXPORTS")
            if fmt == '1':
                filepath = self.data_exporter.export_to_html(item['data'], filename)
            else:
                filepath = self.data_exporter.export_to_json(item['data'], filename)
            
            if filepath:
                exported_files.append(filepath)
        
        if exported_files:
            print(getattr(chalk, 'green').bold(f"\n✔ {len(exported_files)} arquivos exportados com sucesso!"))
            if input(getattr(chalk, 'yellow')("Abrir pasta de exportação? (s/n): ")).lower() == 's':
                os.startfile(Config.HTML_EXPORTS_DIR) if os.name == 'nt' else \
                os.system(f'open "{Config.HTML_EXPORTS_DIR}"' if sys.platform == 'darwin' else \
                f'xdg-open "{Config.HTML_EXPORTS_DIR}"')
        else:
            print(getattr(chalk, 'red')("\n✖ Nenhum arquivo foi exportado"))
            
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def tools_menu(self):
        while True:
            self.ui.show_banner()
            options = [
                ["1", "🔍 Verificar conexão com API"],
                ["2", "📊 Estatísticas do sistema"],
                ["3", "🧹 Otimizar espaço em disco"],
                ["0", "🔙 Voltar"]
            ]
            
            print(tabulate(options, headers=["", ""], tablefmt="fancy_grid"))
            choice = input(getattr(chalk, 'yellow')("\n➤ Selecione uma ferramenta: "))
            
            if choice == '1':
                self.check_api_connection()
            elif choice == '2':
                self.show_system_stats()
            elif choice == '3':
                self.optimize_storage()
            elif choice == '0':
                break
            else:
                print(getattr(chalk, 'red')("\n⚠ Opção inválida!"))
                time.sleep(1)

    def check_api_connection(self):
        self.ui.loading_animation("Testando conexão com API")
        
        try:
            start_time = time.time()
            response = requests.get(self.api_url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status = getattr(chalk, 'green').bold("ONLINE")
                status_msg = getattr(chalk, 'green')("A API está respondendo normalmente")
            else:
                status = getattr(chalk, 'yellow').bold("RESTRITA")
                status_msg = getattr(chalk, 'yellow')(f"A API retornou código {response.status_code}")
                
            print("\n" + getattr(chalk, 'cyan').bold("📡 Status da Conexão:"))
            print(getattr(chalk, 'white')(f"🔗 Endpoint: {self.api_url}"))
            print(getattr(chalk, 'white')(f"🟢 Status: {status}"))
            print(getattr(chalk, 'white')(f"⏱ Tempo de resposta: {response_time:.2f} ms"))
            print(status_msg)
            
        except requests.RequestException as e:
            print("\n" + getattr(chalk, 'red').bold("📡 Status da Conexão:"))
            print(getattr(chalk, 'white')(f"🔗 Endpoint: {self.api_url}"))
            print(getattr(chalk, 'white')(f"🔴 Status: {getattr(chalk, 'red').bold('OFFLINE')}"))
            print(getattr(chalk, 'red')(f"Erro: {e}"))
            
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def show_system_stats(self):
        self.ui.loading_animation("Coletando estatísticas")
        
        def get_dir_size(path):
            return sum(os.path.getsize(os.path.join(path, f)) for f in os.listdir(path)) / (1024 * 1024)
            
        results_count = len(self.file_manager.list_files("RESULTS"))
        html_count = len(self.file_manager.list_files("HTML_EXPORTS"))
        backups_count = len(os.listdir(Config.BACKUP_DIR)) if os.path.exists(Config.BACKUP_DIR) else 0
        
        results_size = get_dir_size(Config.RESULTS_DIR) if os.path.exists(Config.RESULTS_DIR) else 0
        html_size = get_dir_size(Config.HTML_EXPORTS_DIR) if os.path.exists(Config.HTML_EXPORTS_DIR) else 0
        backups_size = get_dir_size(Config.BACKUP_DIR) if os.path.exists(Config.BACKUP_DIR) else 0
        total_size = results_size + html_size + backups_size
        
        history_count = len(self.history)
        
        print("\n" + getattr(chalk, 'cyan').bold("📊 Estatísticas do Sistema\n"))
        
        stats = [
            ["📁 Resultados salvos", f"{results_count} arquivos", f"{results_size:.2f} MB"],
            ["📄 Exportações HTML", f"{html_count} arquivos", f"{html_size:.2f} MB"],
            ["💾 Backups", f"{backups_count} arquivos", f"{backups_size:.2f} MB"],
            ["", getattr(chalk, 'bold')("Total"), f"{getattr(chalk, 'bold')(f'{total_size:.2f} MB')}"],
            ["", "", ""],
            ["⏳ Pesquisas no histórico", f"{history_count}/{Config.MAX_HISTORY}", ""],
            ["🕒 Última pesquisa", 
             self.history[-1]['date'] if self.history else "N/A", 
             ""]
        ]
        
        print(tabulate(stats, tablefmt="simple"))
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def optimize_storage(self):
        self.ui.show_banner()
        print(getattr(chalk, 'cyan').bold("\n🛠️ Otimização de Espaço em Disco\n"))
        
        old_files = []
        threshold = time.time() - (30 * 24 * 60 * 60)
        
        for dir_type in ["RESULTS", "HTML_EXPORTS"]:
            dir_path = getattr(Config, dir_type)
            if os.path.exists(dir_path):
                for f in os.listdir(dir_path):
                    filepath = os.path.join(dir_path, f)
                    if os.path.getmtime(filepath) < threshold:
                        old_files.append(filepath)
        
        total_size = sum(os.path.getsize(f) for f in old_files) / (1024 * 1024)
        
        if not old_files:
            print(getattr(chalk, 'green')("✅ Não há arquivos antigos para limpar (mais de 30 dias)"))
            input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            return
            
        print(getattr(chalk, 'white')(f"🔍 Encontrados {len(old_files)} arquivos antigos (mais de 30 dias)"))
        print(getattr(chalk, 'white')(f"💾 Espaço que pode ser liberado: {total_size:.2f} MB\n"))
        
        confirm = input(getattr(chalk, 'red')("⚠ Deseja remover esses arquivos? (s/n): "))
        if confirm.lower() != 's':
            print(getattr(chalk, 'yellow')("\nOperação cancelada"))
            input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))
            return
            
        self.ui.progress_bar(desc="Limpando arquivos antigos")
        
        failed = 0
        for filepath in old_files:
            try:
                os.remove(filepath)
            except:
                failed += 1
                
        if failed:
            print(getattr(chalk, 'yellow')(f"\n⚠ {failed} arquivos não puderam ser removidos"))
        else:
            print(getattr(chalk, 'green')("\n✅ Limpeza concluída com sucesso!"))
            
        print(getattr(chalk, 'white')(f"🗑️ {len(old_files) - failed} arquivos removidos"))
        print(getattr(chalk, 'white')(f"💾 Espaço liberado: ~{total_size:.2f} MB"))
        
        input(getattr(chalk, 'yellow')("\n⏎ Pressione Enter para continuar..."))

    def run(self):
        while True:
            self.ui.show_banner()
            choice = self.ui.show_menu()
            
            if choice == '1':
                self.run_search_flow()
            elif choice == '2':
                self.show_history()
            elif choice == '3':
                self.manage_results()
            elif choice == '4':
                self.bulk_export()
            elif choice == '5':
                self.tools_menu()
            elif choice == '0':
                print(getattr(chalk, 'magenta').bold("\n✨ Obrigado por usar Quality Midia Search Ultra Pro!"))
                time.sleep(1)
                break
            else:
                print(getattr(chalk, 'red')("\n⚠ Opção inválida!"))
                time.sleep(1)

def check_dependencies():
    required = [
        'requests', 
        'pyfiglet', 
        'halo', 
        'simple_chalk', 
        'tabulate', 
        'tqdm',
        'webbrowser',
        'zipfile'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(getattr(chalk, 'red').bold("\n⚠ Bibliotecas necessárias não encontradas:"))
        for m in missing:
            print(f"- {m}")
        print(getattr(chalk, 'yellow')("\nInstale com: pip install " + " ".join(missing)))
        return False
    return True

if __name__ == "__main__":
    if check_dependencies():
        app = SearchEngine()
        try:
            app.run()
        except KeyboardInterrupt:
            print(getattr(chalk, 'red').bold("\n\n🔌 Programa interrompido pelo usuário"))
            time.sleep(1)
        except Exception as e:
            print(getattr(chalk, 'red').bold(f"\n⚠ Erro crítico: {e}"))
            time.sleep(2)