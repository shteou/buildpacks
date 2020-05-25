pip uninstall -y buildpacks
python3 setup.py sdist bdist_wheel
#python setup.py  build
pip install dist/buildpacks-0.0.1-py3-none-any.whl
