import os
import zipfile

def bdist_wheel(pkg_dir, dist_dir):
    """Create a wheel file from a package directory."""
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    wheel_name = f"{os.path.basename(pkg_dir)}-0.1.0-py3-none-any.whl"
    wheel_path = os.path.join(dist_dir, wheel_name)
    
    with zipfile.ZipFile(wheel_path, 'w') as zipf:
        for root, dirs, files in os.walk(pkg_dir):
            for file in files:
                zipf.write(os.path.join(root, file), file)
    
    return wheel_path
