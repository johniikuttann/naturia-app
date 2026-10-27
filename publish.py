"""Publish a new app version in this repository: copy the APK and refresh the README.

    python publish.py C:\\path\\to\\Naturia.apk 2.1.0

Then commit and push. (Keep the naturia-server repository in step too: see publish_apk.py there.)
"""
import hashlib
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    source, version = sys.argv[1], sys.argv[2]
    if not re.fullmatch(r'\d+(\.\d+){1,3}', version):
        sys.exit(f'The version must look like 2.1.0, not "{version}".')
    try:
        with zipfile.ZipFile(source) as apk:
            manifest = apk.read('AndroidManifest.xml')
            has_code = any(n.startswith('classes') and n.endswith('.dex') for n in apk.namelist())
    except (OSError, KeyError, zipfile.BadZipFile):
        sys.exit(f'"{source}" is not an APK file.')
    if not has_code:
        sys.exit('That file has no app code in it: it does not look like an APK.')
    if version.encode('utf-16-le') not in manifest:
        sys.exit(f'The APK\'s own version number is not {version}. Check versionName and try again.')

    target = os.path.join(HERE, 'Naturia.apk')
    shutil.copyfile(source, target)
    with open(target, 'rb') as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    size_mb = os.path.getsize(target) / 1_000_000

    readme_path = os.path.join(HERE, 'README.md')
    with open(readme_path, encoding='utf-8') as f:
        readme = f.read()
    readme, n_version = re.subn(r'\(version [\d.]+, [\d.]+ MB\)', f'(version {version}, {size_mb:.1f} MB)', readme)
    readme, n_hash = re.subn(r'\b[0-9a-f]{64}\b', digest, readme)
    if n_version != 1 or n_hash != 1:
        sys.exit('README.md no longer has its version line and SHA-256 line in the expected form. Fix it by hand.')
    with open(readme_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(readme)
    print(f'Published version {version}: Naturia.apk ({size_mb:.1f} MB, sha256 {digest[:12]}...) and README updated.')
    print('Next: git add -A && git commit -m "Naturia app ' + version + '" && git push')


if __name__ == '__main__':
    main()
