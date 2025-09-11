# SAIA Data Directory

This directory contains data files, samples, and resources used by the SAIA Business Management System.

## Directory Structure

### 📄 samples/
Sample data files and examples:
- **sample_knowledge_content.txt** - Sample knowledge base content for reference

### 🏢 wazen/
Wazen company-specific data files:
- **wazen content.docx** - Original Wazen content document
- **wazen-data.md** - Wazen data in Markdown format
- **FAQ.docx** - Wazen FAQ document

### 🗄️ sql/
SQL scripts and database-related files:
- **init-db.sql** - Database initialization script

## Usage Guidelines

### Sample Data
The samples directory contains reference files that can be used as templates for:
- Knowledge base content structure
- Data import formats
- Configuration examples

### Company Data
Company-specific data should be organized in subdirectories by company name:
- Use lowercase company names for directory names
- Include all relevant documents and data files
- Maintain original file formats when possible

### SQL Scripts
Database scripts should be:
- Well-documented with comments
- Tested before deployment
- Versioned if they modify existing schemas

## File Formats

### Supported Formats
- **Markdown (.md)** - Preferred for text content
- **Word Documents (.docx)** - For original documents
- **SQL (.sql)** - For database scripts
- **Text (.txt)** - For simple data files
- **CSV (.csv)** - For tabular data

### Best Practices
1. **Use descriptive filenames** that indicate content and purpose
2. **Include creation/modification dates** in filenames when relevant
3. **Maintain original documents** alongside processed versions
4. **Document file purposes** in this README when adding new files

## Adding New Data

When adding new data files:

1. **Choose appropriate subdirectory** based on purpose
2. **Create company subdirectories** for company-specific data
3. **Use consistent naming conventions**
4. **Update this README** with new file descriptions
5. **Include metadata** about file sources and purposes

## Data Security

### Sensitive Information
- **Never commit** sensitive data like passwords or API keys
- **Use environment variables** for configuration
- **Sanitize data** before committing to version control
- **Follow company data policies** for customer information

### Access Control
- Ensure proper file permissions
- Limit access to sensitive company data
- Use encryption for confidential documents
- Regular backup of important data files

## Maintenance

### Regular Tasks
- Review and update outdated data files
- Clean up temporary or obsolete files
- Verify data integrity and format consistency
- Update documentation when structure changes

### File Lifecycle
1. **Creation** - Add with proper documentation
2. **Usage** - Track which scripts/processes use the file
3. **Updates** - Version control for significant changes
4. **Archival** - Move obsolete files to archive directory
5. **Deletion** - Remove when no longer needed
