# PyLibrary Management System

A comprehensive library management system built with Django, featuring both main library and e-library seat management capabilities.

## 📚 Features

- **Main Library Management**: Track student entry/exit times
- **E-Library Management**: Seat reservation and session tracking
- **Student Management**: Department-wise student organization
- **Real-time Dashboard**: Analytics and reporting
- **User Authentication**: Secure login system
- **Responsive Design**: Mobile-friendly interface

## 🚀 Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start development server: `python manage.py runserver`

---

## 🎨 Contributing to Frontend Templates

### Overview
Our frontend is built using Django templates with AdminLTE 3 theme, Bootstrap 5, and modern JavaScript libraries. We follow a component-based approach for maintainable and reusable templates.

### 📁 Template Structure

```
templates/
├── base.html                 # Main layout template
├── utils/
│   ├── sidebar_menu.html    # Navigation menu
│   └── footer.html          # Footer component
├── auth/                    # Authentication templates
├── dashboard/               # Dashboard templates
├── library/                 # Library management templates
├── reports/                 # Reporting templates
├── tickets/                 # Support ticket templates
└── users/                   # User management templates
```

### 🛠️ Technologies Used

#### CSS Frameworks & Libraries
- **Bootstrap 5.3+**: Primary CSS framework
- **AdminLTE 3**: Admin dashboard theme
- **Font Awesome 6**: Icon library
- **DataTables**: Advanced table functionality
- **DateRangePicker**: Date selection components

#### JavaScript Libraries
- **jQuery 3.6+**: DOM manipulation
- **Chart.js**: Data visualization
- **Axios**: HTTP client
- **SweetAlert2**: Beautiful alerts
- **Moment.js**: Date manipulation

### 🎯 Design Guidelines

#### 1. Consistent Color Palette
```css
/* Primary Colors */
--primary: #007bff;
--secondary: #6c757d;
--success: #28a745;
--info: #17a2b8;
--warning: #ffc107;
--danger: #dc3545;

/* Sidebar Themes */
--sidebar-navy: #2c3e50;
--sidebar-teal: #16a085;
--sidebar-maroon: #8e44ad;
```

#### 2. Typography Standards
- **Headings**: Use semantic HTML (h1-h6)
- **Body Text**: 14px base font size
- **Code**: Use `<code>` tags with monospace font
- **Labels**: Bootstrap `.form-label` class

#### 3. Component Naming Convention
- Use BEM methodology: `.block__element--modifier`
- Prefix custom classes with `py-` (e.g., `py-card`, `py-sidebar`)
- Follow Bootstrap utilities where possible

### 📝 Template Development Guidelines

#### 1. Base Template Structure
All templates should extend `base.html`:

```django
{% extends "base.html" %}
{% load static %}

{% block title %}Page Title - {{ APP_NAME }}{% endblock %}

{% block content_header %}Page Header{% endblock %}

{% block breadcrumb %}
    <li class="breadcrumb-item"><a href="/">Home</a></li>
    <li class="breadcrumb-item active">Current Page</li>
{% endblock %}

{% block content %}
    <!-- Your content here -->
{% endblock %}

{% block customCss %}
    <!-- Page-specific CSS -->
{% endblock %}

{% block customJs %}
    <!-- Page-specific JavaScript -->
{% endblock %}
```

#### 2. Form Guidelines
```django
<!-- Use Bootstrap form classes -->
<form method="post" class="needs-validation" novalidate>
    {% csrf_token %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Form Title</h3>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <div class="form-group">
                        <label for="id_field" class="form-label">Field Label</label>
                        <input type="text" class="form-control" id="id_field" name="field" required>
                        <div class="invalid-feedback">
                            Please provide a valid input.
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="card-footer">
            <button type="submit" class="btn btn-primary">Submit</button>
            <a href="#" class="btn btn-secondary">Cancel</a>
        </div>
    </div>
</form>
```

#### 3. Table Guidelines
```django
<!-- Use DataTables for enhanced functionality -->
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Data Table</h3>
        <div class="card-tools">
            <a href="#" class="btn btn-primary btn-sm">
                <i class="fas fa-plus"></i> Add New
            </a>
        </div>
    </div>
    <div class="card-body">
        <table id="dataTable" class="table table-bordered table-striped">
            <thead>
                <tr>
                    <th>Column 1</th>
                    <th>Column 2</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <!-- Table data -->
            </tbody>
        </table>
    </div>
</div>
```

### 🔧 Development Workflow

#### 1. Setting Up Development Environment
```bash
# Navigate to project directory
cd PyLibrary

# Collect static files
python manage.py collectstatic --noinput

# Start development server
python manage.py runserver
```

#### 2. Making Template Changes
1. **Create/Edit Templates**: Work in the `templates/` directory
2. **Test Locally**: Use Django development server
3. **Check Responsiveness**: Test on different screen sizes
4. **Validate HTML**: Ensure semantic and accessible markup
5. **Test JavaScript**: Check console for errors

#### 3. Best Practices
- **Mobile First**: Design for mobile, enhance for desktop
- **Accessibility**: Use ARIA labels and semantic HTML
- **Performance**: Minimize HTTP requests and optimize images
- **SEO**: Use proper meta tags and structured data
- **Security**: Always use CSRF tokens in forms

### 📱 Responsive Design Standards

#### Breakpoints
```css
/* Extra small devices (phones) */
@media (max-width: 575.98px) { ... }

/* Small devices (landscape phones) */
@media (min-width: 576px) and (max-width: 767.98px) { ... }

/* Medium devices (tablets) */
@media (min-width: 768px) and (max-width: 991.98px) { ... }

/* Large devices (desktops) */
@media (min-width: 992px) and (max-width: 1199.98px) { ... }

/* Extra large devices (large desktops) */
@media (min-width: 1200px) { ... }
```

#### Grid System
- Use Bootstrap's 12-column grid system
- Stack columns on smaller screens
- Use responsive utilities (`.d-none`, `.d-md-block`, etc.)

### 🎨 Component Library

#### 1. Cards
```django
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Card Title</h3>
        <div class="card-tools">
            <!-- Card tools -->
        </div>
    </div>
    <div class="card-body">
        <!-- Card content -->
    </div>
    <div class="card-footer">
        <!-- Card footer -->
    </div>
</div>
```

#### 2. Alerts
```django
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            <i class="fas fa-info-circle mr-2"></i>
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    {% endfor %}
{% endif %}
```

#### 3. Modals
```django
<div class="modal fade" id="exampleModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Modal Title</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Modal content -->
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary">Save</button>
            </div>
        </div>
    </div>
</div>
```

### 🔍 Testing Guidelines

#### 1. Browser Testing
- **Chrome** (latest)
- **Firefox** (latest)
- **Safari** (latest)
- **Edge** (latest)

#### 2. Device Testing
- **Mobile**: iPhone, Android phones
- **Tablet**: iPad, Android tablets
- **Desktop**: Various screen resolutions

#### 3. Accessibility Testing
- Use screen readers
- Test keyboard navigation
- Check color contrast ratios
- Validate with WAVE tool

### 📋 Contribution Checklist

Before submitting your frontend changes:

- [ ] **Responsive Design**: Works on all screen sizes
- [ ] **Cross-browser**: Tested on major browsers
- [ ] **Accessibility**: WCAG 2.1 AA compliant
- [ ] **Performance**: No console errors
- [ ] **Code Quality**: Clean, commented code
- [ ] **Documentation**: Update README if needed
- [ ] **Testing**: All functionality works correctly

### 🤝 Getting Help

- **Documentation**: Check Django and Bootstrap docs
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: All changes require review

### 📚 Useful Resources

- [Django Template Documentation](https://docs.djangoproject.com/en/stable/topics/templates/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [AdminLTE 3 Documentation](https://adminlte.io/docs/3.2/)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

---

*Happy coding! 🚀*