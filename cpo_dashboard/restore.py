import json
import re

transcript_path = r'C:\Users\user\.gemini\antigravity\brain\e49e51f8-71de-4c56-aeaa-085095198c48\.system_generated\logs\transcript_full.jsonl'
skip_files = ['manajemen_pengguna.py', 'utils.py']

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'VIEW_FILE':
            content = data.get('content', '')
            if 'File Path: ' in content:
                path_part = content.split('File Path: ')[1].split('\n')[0]
                # Clean up backticks and protocol without using literal backtick char
                filepath = re.sub(r'[^a-zA-Z0-9_.:/\\]', '', path_part)
                filepath = filepath.replace('file:///', '').replace('/', '\\\\')
                if any(skip in filepath for skip in skip_files):
                    continue
                
                lines = content.split('\n')
                code_lines = []
                started = False
                for l in lines:
                    if 'The following code has been modified' in l:
                        started = True
                        continue
                    if started:
                        if l.startswith('The above content shows'): break
                        if l.startswith('The above content does NOT show'): break
                        # extract original line, split by first ': '
                        parts = l.split(': ', 1)
                        if len(parts) == 2 and parts[0].isdigit():
                            code_lines.append(parts[1])
                        elif l.endswith(':'):
                            code_lines.append('')
                if code_lines:
                    try:
                        with open(filepath, 'w', encoding='utf-8') as out:
                            out.write('\n'.join(code_lines))
                        print(f'Restored {filepath}')
                    except Exception as e:
                        print(f'Error restoring {filepath}: {e}')
