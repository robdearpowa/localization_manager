echo "Removing old dist folder"
rm dist/ -r
echo "Removing old build folder"
rm build/ -r
python -m PyInstaller localization_manager_qt.spec