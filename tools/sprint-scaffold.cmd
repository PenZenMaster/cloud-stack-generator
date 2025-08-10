cd E:\projects\cloud-stack-generator

rem Create core architecture directories
mkdir src\core\config
mkdir src\core\generators  
mkdir src\core\data
mkdir src\core\utils

rem Create UI component directories
mkdir src\ui\components
mkdir src\ui\content_tabs
mkdir src\ui\widgets

rem Create template directories
mkdir src\templates\base
mkdir src\templates\professional

rem Create test directories
mkdir tests\unit
mkdir tests\integration

rem Create __init__.py files for Python packages
echo. > src\core\__init__.py
echo. > src\core\config\__init__.py
echo. > src\core\generators\__init__.py
echo. > src\core\data\__init__.py
echo. > src\core\utils\__init__.py
echo. > src\ui\components\__init__.py
echo. > src\ui\content_tabs\__init__.py
echo. > src\ui\widgets\__init__.py
echo. > tests\__init__.py
echo. > tests\unit\__init__.py
echo. > tests\integration\__init__.py