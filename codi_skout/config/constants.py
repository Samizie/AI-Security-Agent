# Define file patterns to look for

import re

# Security-sensitive file patterns
SECURITY_PATTERNS = [
    # Environment and configuration files
    '.env', '.env.local', '.env.development', '.env.production', '.env.staging',
    '.envrc', 'environment.yml', 'config.py', 'settings.py', 'configuration.py',
    'app.config', 'web.config', 'appsettings.json', 'appsettings.*.json',
    'application.properties', 'application.yml', 'application.yaml',
    'config.json', 'config.xml', 'config.toml', 'config.ini',
    
    # Secrets and keys
    'secret', 'secrets', 'key', 'keys', 'password', 'passwords',
    'credentials', 'auth', 'token', 'tokens', 'cert', 'certificate',
    'private_key', 'public_key', 'keystore', 'truststore',
    '.secrets', '.credentials', '.auth', '.token',
    'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519',
    
    # Docker and containerization
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    'docker-compose.override.yml', '.dockerignore', 'Dockerfile.*',
    'kubernetes.yml', 'k8s.yml', 'deployment.yml', 'service.yml',
    'ingress.yml', 'configmap.yml', 'secret.yml',
    
    # Package management and dependencies
    'requirements.txt', 'requirements-dev.txt', 'requirements-prod.txt',
    'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'Pipfile', 'Pipfile.lock', 'poetry.lock', 'pyproject.toml',
    'Gemfile', 'Gemfile.lock', 'composer.json', 'composer.lock',
    'go.mod', 'go.sum', 'Cargo.toml', 'Cargo.lock',
    'pom.xml', 'build.gradle', 'build.gradle.kts', 'gradle.properties',
    'mix.exs', 'mix.lock', 'deps.edn', 'project.clj',
    
    # Database configurations
    'database.yml', 'db.json', 'database.json', 'db.config',
    'connection.json', 'datasource.xml', 'hibernate.cfg.xml',
    'schema.sql', 'seeds.sql', 'migrations',
    
    # Cloud and infrastructure
    'terraform.tfvars', '*.tfvars', 'cloudformation.yml', 'cloudformation.yaml',
    'serverless.yml', 'serverless.yaml', 'sam.yml', 'sam.yaml',
    'ansible.yml', 'playbook.yml', 'inventory.yml',
    
    # Security-specific files
    'security.xml', 'security.json', 'auth.json', 'oauth.json',
    'jwt.json', 'saml.xml', 'ldap.json', 'acl.json',
    'roles.json', 'permissions.json', 'policy.json',
    
    # SSL/TLS certificates
    '*.pem', '*.crt', '*.cer', '*.p12', '*.pfx', '*.jks',
    'ca-bundle.crt', 'server.crt', 'client.crt'
]

# URL/Route definition files
URL_PATTERNS = [
    # Python frameworks
    'routes.py', 'urls.py', 'app.py', 'main.py', 'server.py',
    'views.py', 'handlers.py', 'controllers.py', 'api.py',
    'wsgi.py', 'asgi.py', 'fastapi_app.py', 'flask_app.py',
    'tornado_app.py', 'bottle_app.py', 'cherrypy_app.py',
    
    # JavaScript/Node.js
    'index.js', 'app.js', 'server.js', 'router.js', 'routes.js',
    'api.js', 'controllers.js', 'handlers.js', 'middleware.js',
    'express.js', 'koa.js', 'fastify.js', 'hapi.js',
    'index.ts', 'app.ts', 'server.ts', 'router.ts', 'routes.ts',
    
    # Java frameworks
    'Controller.java', 'RestController.java', 'WebConfig.java',
    'RouterConfig.java', 'EndpointConfig.java', 'ApiConfig.java',
    'ServletConfig.java', 'FilterConfig.java',
    
    # PHP frameworks
    'routes.php', 'web.php', 'api.php', 'index.php',
    'router.php', 'controller.php', 'handlers.php',
    
    # Ruby frameworks
    'routes.rb', 'config.ru', 'application.rb', 'routes_config.rb',
    'controller.rb', 'api.rb', 'handlers.rb',
    
    # Go frameworks
    'routes.go', 'handlers.go', 'controllers.go', 'server.go',
    'router.go', 'api.go', 'main.go',
    
    # C# frameworks
    'Startup.cs', 'Program.cs', 'Controllers.cs', 'ApiController.cs',
    'RouteConfig.cs', 'WebApiConfig.cs',
    
    # Rust frameworks
    'routes.rs', 'handlers.rs', 'controllers.rs', 'server.rs',
    'main.rs', 'api.rs',
    
    # Other languages
    'routes.scala', 'routes.kt', 'routes.swift', 'routes.dart',
    'routes.ex', 'routes.exs', 'router.ex', 'router.exs'
]

# Programming language file extensions
CODE_EXTENSIONS = [
    # Popular languages
    '.py', '.js', '.ts', '.java', '.php', '.rb', '.go', '.rs', '.cpp', '.cs',
    
    # Web technologies
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.jsx', '.tsx',
    '.vue', '.svelte', '.astro',
    
    # Mobile development
    '.swift', '.kt', '.dart', '.m', '.mm', '.h', '.hpp',
    
    # Functional languages
    '.scala', '.clj', '.cljs', '.hs', '.ml', '.fsx', '.fs',
    
    # System languages
    '.c', '.cc', '.cxx', '.cpp', '.hpp', '.hxx', '.h++',
    
    # Scripting languages
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
    '.perl', '.pl', '.r', '.R', '.lua', '.vim',
    
    # Data and markup
    '.sql', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini',
    '.md', '.rst', '.tex',
    
    # Other languages
    '.ex', '.exs', '.erl', '.jl', '.nim', '.crystal', '.cr',
    '.zig', '.d', '.ada', '.adb', '.ads', '.f90', '.f95', '.f03',
    '.cob', '.cbl', '.pas', '.pp', '.lpr'
]

# Comprehensive endpoint detection patterns
ENDPOINT_PATTERNS = [
    # Python - Flask
    r'@app\.route\([\'"]([^\'"]+)',
    r'@bp\.route\([\'"]([^\'"]+)',
    r'add_url_rule\([\'"]([^\'"]+)',
    
    # Python - Django
    r'path\([\'"]([^\'"]+)',
    r'url\([\'"]([^\'"]+)',
    r're_path\([\'"]([^\'"]+)',
    r'django\.urls\.path\([\'"]([^\'"]+)',
    
    # Python - FastAPI
    r'@app\.(get|post|put|delete|patch|head|options|trace)\([\'"]([^\'"]+)',
    r'@router\.(get|post|put|delete|patch|head|options|trace)\([\'"]([^\'"]+)',
    r'APIRouter\(\)\.(?:get|post|put|delete|patch|head|options|trace)\([\'"]([^\'"]+)',
    
    # Python - Tornado
    r'\(r[\'"]([^\'"]+)[\'"],\s*\w+Handler\)',
    
    # JavaScript/Node.js - Express
    r'app\.(get|post|put|delete|patch|head|options|all)\([\'"]([^\'"]+)',
    r'router\.(get|post|put|delete|patch|head|options|all)\([\'"]([^\'"]+)',
    r'express\(\)\.(get|post|put|delete|patch|head|options|all)\([\'"]([^\'"]+)',
    
    # JavaScript/Node.js - Koa
    r'router\.(get|post|put|delete|patch|head|options|all)\([\'"]([^\'"]+)',
    r'\.get\([\'"]([^\'"]+)',
    r'\.post\([\'"]([^\'"]+)',
    
    # JavaScript/Node.js - Fastify
    r'fastify\.(get|post|put|delete|patch|head|options)\([\'"]([^\'"]+)',
    r'server\.(get|post|put|delete|patch|head|options)\([\'"]([^\'"]+)',
    
    # JavaScript/Node.js - Hapi
    r'server\.route\(\s*\{\s*method:\s*[\'"](?:GET|POST|PUT|DELETE|PATCH)[\'"],\s*path:\s*[\'"]([^\'"]+)',
    
    # Java - Spring Boot
    r'@(?:Get|Post|Put|Delete|Patch|Request)Mapping\([\'"]([^\'"]+)',
    r'@RequestMapping\([\'"]([^\'"]+)',
    r'@PathVariable\([\'"]([^\'"]+)',
    
    # Java - JAX-RS
    r'@Path\([\'"]([^\'"]+)',
    r'@GET\s+@Path\([\'"]([^\'"]+)',
    r'@POST\s+@Path\([\'"]([^\'"]+)',
    
    # PHP - Laravel
    r'Route::(get|post|put|delete|patch|options|any)\([\'"]([^\'"]+)',
    r'router->(get|post|put|delete|patch|options|any)\([\'"]([^\'"]+)',
    
    # PHP - Symfony
    r'@Route\([\'"]([^\'"]+)',
    r'#\[Route\([\'"]([^\'"]+)',
    
    # Ruby - Rails
    r'(?:get|post|put|delete|patch|head|options)\s+[\'"]([^\'"]+)',
    r'match\s+[\'"]([^\'"]+)',
    r'resources?\s+:(\w+)',
    
    # Ruby - Sinatra
    r'(?:get|post|put|delete|patch|head|options)\s+[\'"]([^\'"]+)',
    
    # Go - Gin
    r'r\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\([\'"]([^\'"]+)',
    r'router\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\([\'"]([^\'"]+)',
    
    # Go - Echo
    r'e\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\([\'"]([^\'"]+)',
    r'echo\.(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\([\'"]([^\'"]+)',
    
    # Go - Gorilla Mux
    r'r\.HandleFunc\([\'"]([^\'"]+)',
    r'\.Path\([\'"]([^\'"]+)',
    
    # C# - ASP.NET Core
    r'\[Route\([\'"]([^\'"]+)',
    r'\[HttpGet\([\'"]([^\'"]+)',
    r'\[HttpPost\([\'"]([^\'"]+)',
    r'MapGet\([\'"]([^\'"]+)',
    r'MapPost\([\'"]([^\'"]+)',
    
    # C# - Web API
    r'app\.Map(?:Get|Post|Put|Delete|Patch)\([\'"]([^\'"]+)',
    
    # Rust - Actix
    r'web::(?:get|post|put|delete|patch|head|options)\(\)\.(to|service)\([\'"]([^\'"]+)',
    r'HttpServer::new\(\)\.route\([\'"]([^\'"]+)',
    
    # Rust - Warp
    r'warp::path\([\'"]([^\'"]+)',
    r'\.and\(warp::path\([\'"]([^\'"]+)',
    
    # Scala - Play Framework
    r'(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+[\'"]([^\'"]+)',
    
    # Kotlin - Ktor
    r'(?:get|post|put|delete|patch|head|options)\([\'"]([^\'"]+)',
    r'route\([\'"]([^\'"]+)',
    
    # Elixir - Phoenix
    r'(?:get|post|put|delete|patch|head|options)\s+[\'"]([^\'"]+)',
    r'resources\s+[\'"]([^\'"]+)',
    
    # Swift - Vapor
    r'app\.(?:get|post|put|delete|patch|head|options)\([\'"]([^\'"]+)',
    r'router\.(?:get|post|put|delete|patch|head|options)\([\'"]([^\'"]+)',
    
    # Generic patterns for route definitions
    r'route\([\'"]([^\'"]+)',
    r'path\([\'"]([^\'"]+)',
    r'url\([\'"]([^\'"]+)',
    r'endpoint\([\'"]([^\'"]+)',
    r'api\([\'"]([^\'"]+)',
]

# Framework-specific configuration files
FRAMEWORK_CONFIGS = {
    'django': ['settings.py', 'urls.py', 'wsgi.py', 'asgi.py', 'manage.py'],
    'flask': ['app.py', 'config.py', 'requirements.txt', 'wsgi.py'],
    'fastapi': ['main.py', 'app.py', 'requirements.txt', 'uvicorn.py'],
    'express': ['app.js', 'server.js', 'package.json', 'routes/', 'middleware/'],
    'spring': ['pom.xml', 'application.properties', 'application.yml', 'build.gradle'],
    'laravel': ['composer.json', 'artisan', 'config/', 'routes/', 'app/Http/'],
    'rails': ['Gemfile', 'config.ru', 'config/', 'app/controllers/'],
    'gin': ['go.mod', 'main.go', 'routes.go', 'handlers.go'],
    'aspnet': ['*.csproj', 'Program.cs', 'Startup.cs', 'appsettings.json'],
    'actix': ['Cargo.toml', 'main.rs', 'routes.rs', 'handlers.rs'],
    'phoenix': ['mix.exs', 'config/', 'lib/', 'router.ex'],
    'vapor': ['Package.swift', 'main.swift', 'routes.swift']
}

# Common security headers and middleware patterns
SECURITY_MIDDLEWARE_PATTERNS = [
    r'@require_auth',
    r'@login_required',
    r'@authenticated',
    r'@permission_required',
    r'@roles_required',
    r'middleware\([\'"]auth[\'"]',
    r'middleware\([\'"]permission[\'"]',
    r'@PreAuthorize',
    r'@Secured',
    r'@RolesAllowed',
    r'authenticate\(',
    r'authorize\(',
    r'checkPermission\(',
    r'verifyToken\(',
    r'validateJWT\(',
]

# API versioning patterns
API_VERSION_PATTERNS = [
    r'/v\d+/',
    r'/api/v\d+/',
    r'version\s*=\s*[\'"]v?\d+[\'"]',
    r'@ApiVersion\([\'"]v?\d+[\'"]',
    r'accept-version:\s*v?\d+',
]

# HTTP method patterns for endpoint detection
HTTP_METHODS = [
    'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'TRACE', 'CONNECT'
]

# Common endpoint prefixes that indicate API endpoints
API_PREFIXES = [
    '/api/', '/v1/', '/v2/', '/v3/', '/rest/', '/graphql/', '/websocket/',
    '/admin/', '/dashboard/', '/auth/', '/oauth/', '/login/', '/logout/',
    '/register/', '/users/', '/user/', '/account/', '/profile/', '/settings/'
]

# File patterns that might contain hardcoded secrets
POTENTIAL_SECRET_FILES = [
    r'.*\.backup$',
    r'.*\.bak$',
    r'.*\.old$',
    r'.*\.orig$',
    r'.*\.tmp$',
    r'.*\.temp$',
    r'.*\.log$',
    r'.*\.dump$',
    r'.*\.sql$',
    r'.*\.db$',
    r'.*\.sqlite$',
    r'.*\.sqlite3$',
]




























# SECURITY_PATTERNS = [
#     '.env', 'config.py', 'settings.py', 'secret', 'key', 'password',
#     'docker-compose.yml', 'Dockerfile', 'requirements.txt', 'package.json'
# ]

# URL_PATTERNS = [
#     'routes.py', 'urls.py', 'app.py', 'main.py', 'server.py',
#     'index.js', 'router.js', 'api.py'
# ]

# CODE_EXTENSIONS = ['.py', '.js', '.java', '.php', '.rb', '.go', '.rs', '.cpp', '.cs']

# ENDPOINT_PATTERNS = [
#     r'@app\.route\([\'"]([^\'"]+)',  # Flask
#     r'path\([\'"]([^\'"]+)',         # Django
#     r'router\.[get|post|put|delete]+\([\'"]([^\'"]+)',  # Express.js
#     r'@[A-Za-z]*Mapping\([\'"]([^\'"]+)',  # Spring Boot
# ]