# SAIA Scripts Directory

This directory contains utility scripts organized by purpose to help with various aspects of the SAIA Business Management System.

## Directory Structure

### 📊 data_management/
Scripts for managing data import, export, and content management:

- **add_knowledge_content.py** - Add knowledge base content for AI assistants
- **add_knowledge_example.py** - Example script for adding knowledge content
- **add_wazen_content.py** - Specific script for adding Wazen company content
- **import_from_csv.py** - Import data from CSV files
- **import_wazen_faqs.py** - Import Wazen FAQ content

### ⚙️ setup/
Scripts for system setup and configuration:

- **setup_wazen_customer.py** - Set up Wazen customer account and configuration
- **cleanup_codebase.py** - Clean up and organize codebase files

### 🧪 testing/
Scripts for testing and validation:

- **test_improvements.py** - Test system improvements and functionality

## Usage Guidelines

### Running Scripts
All scripts should be run from the project root directory:

```bash
# From project root
cd /path/to/SAIA-Wazen
python scripts/data_management/script_name.py
```

### Environment Setup
Ensure your Django environment is properly configured before running scripts:

```bash
# Activate virtual environment
source venv/bin/activate

# Set Django settings module
export DJANGO_SETTINGS_MODULE=saia.settings

# Or run with Django management command
python manage.py shell < scripts/data_management/script_name.py
```

### Data Management Scripts

#### Knowledge Content Management
```bash
# Add general knowledge content
python scripts/data_management/add_knowledge_content.py

# Add Wazen-specific content
python scripts/data_management/add_wazen_content.py

# Import FAQ content
python scripts/data_management/import_wazen_faqs.py
```

#### Data Import
```bash
# Import from CSV files
python scripts/data_management/import_from_csv.py
```

### Setup Scripts

#### Customer Setup
```bash
# Set up Wazen customer
python scripts/setup/setup_wazen_customer.py

# Clean up codebase
python scripts/setup/cleanup_codebase.py
```

### Testing Scripts

#### System Testing
```bash
# Run improvement tests
python scripts/testing/test_improvements.py
```

## Best Practices

1. **Always backup data** before running data management scripts
2. **Test scripts in development** environment first
3. **Check script documentation** within each file for specific usage instructions
4. **Use virtual environment** to avoid dependency conflicts
5. **Run from project root** to ensure proper Django setup

## Adding New Scripts

When adding new scripts:

1. Place them in the appropriate subdirectory based on purpose
2. Add proper documentation and usage instructions
3. Include error handling and logging
4. Update this README with the new script information
5. Follow the existing naming conventions

## Dependencies

Most scripts require:
- Django environment properly configured
- Database connections established
- Required Python packages installed (see requirements.txt)
- Proper permissions for file operations

## Troubleshooting

Common issues and solutions:

- **Django not found**: Ensure virtual environment is activated
- **Database connection errors**: Check database configuration in settings.py
- **Permission errors**: Ensure proper file permissions and user access
- **Import errors**: Run scripts from project root directory
