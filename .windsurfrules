# CodeAgent Project Rules & Guidelines

## 1. Code Style & Formatting

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters (Black formatter standard)
- Use type hints for all function parameters and return values
- Use Google-style docstrings for all public functions and classes
- Sort imports using isort with the following groups:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports

### JavaScript/TypeScript
- Use 2 spaces for indentation
- Use single quotes for strings
- Always include semicolons
- Use ES6+ syntax
- Follow the Airbnb JavaScript Style Guide
- Use TypeScript for all new components

### SQL
- Use UPPERCASE for SQL keywords
- Indent subqueries and JOIN conditions
- Use snake_case for table and column names
- Include comments for complex queries

## 2. Git Workflow

### Branch Naming
- `feature/`: New features or enhancements
- `bugfix/`: Bug fixes
- `hotfix/`: Critical production fixes
- `chore/`: Maintenance tasks, dependency updates
- `docs/`: Documentation updates
- `test/`: Test-related changes

### Commit Messages
- Use the conventional commits specification:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `style:` for formatting changes
  - `refactor:` for code changes that neither fix bugs nor add features
  - `perf:` for performance improvements
  - `test:` for adding or modifying tests
  - `chore:` for maintenance tasks
- Keep the subject line under 50 characters
- Include a blank line between the subject and body
- Use the body to explain what and why, not how

Example:
```
feat: add user authentication endpoints

- Add login and register endpoints
- Implement JWT token generation
- Add input validation
```

## 3. Testing

### Unit Tests
- Write tests for all new features and bug fixes
- Follow the Arrange-Act-Assert pattern
- Keep tests focused and independent
- Mock external dependencies
- Aim for at least 80% code coverage

### Integration Tests
- Test API endpoints with real database connections
- Use test containers for database testing
- Clean up test data after each test
- Test both success and error cases

### E2E Tests
- Use Playwright for browser automation
- Test critical user journeys
- Run in headless mode in CI

## 4. API Design

### RESTful Endpoints
- Use plural nouns for resources (e.g., `/users`, `/projects`)
- Use HTTP methods appropriately:
  - `GET`: Retrieve resources
  - `POST`: Create resources
  - `PUT`: Update resources (full update)
  - `PATCH`: Partially update resources
  - `DELETE`: Remove resources
- Use kebab-case for URLs (e.g., `/api/v1/user-profiles`)
- Version your API in the URL (e.g., `/api/v1/...`)
- Return appropriate HTTP status codes
- Use consistent response formats:
  ```json
  {
    "data": {},
    "meta": {},
    "error": null
  }
  ```

### Error Handling
- Return meaningful error messages
- Include error codes for client-side handling
- Log detailed error information server-side
- Use HTTP status codes correctly:
  - 400: Bad Request
  - 401: Unauthorized
  - 403: Forbidden
  - 404: Not Found
  - 422: Unprocessable Entity
  - 500: Internal Server Error

## 5. Database

### Schema Changes
- Use Alembic for database migrations
- Write idempotent migration scripts
- Include both `upgrade` and `downgrade` paths
- Test migrations in a staging environment before production
- Never modify production databases directly

### Query Optimization
- Use indexes for frequently queried columns
- Avoid N+1 query problems
- Use `EXPLAIN ANALYZE` for slow queries
- Consider read replicas for read-heavy workloads

## 6. Security

### Authentication & Authorization
- Use JWT for stateless authentication
- Implement role-based access control (RBAC)
- Store sensitive data securely using environment variables
- Rotate secrets regularly
- Implement rate limiting

### Input Validation
- Validate all user input
- Use Pydantic models for request/response validation
- Sanitize output to prevent XSS attacks
- Use parameterized queries to prevent SQL injection

## 7. Documentation

### Code Documentation
- Document all public APIs
- Include examples in docstrings
- Keep README files up to date
- Document environment variables

### API Documentation
- Use OpenAPI/Swagger for API documentation
- Include request/response examples
- Document authentication requirements
- Include error responses

## 8. Performance

### Frontend
- Implement code splitting
- Optimize asset loading
- Use lazy loading for routes and components
- Minimize bundle size

### Backend
- Implement caching where appropriate
- Use background tasks for long-running operations
- Optimize database queries
- Monitor and optimize memory usage

## 9. Development Workflow

### Local Development
- Use Docker for local development
- Keep the local environment as close to production as possible
- Document setup instructions in the README
- Use environment variables for configuration

### Code Reviews
- At least one approval required before merging
- Use GitHub Pull Requests
- Keep PRs focused and small
- Include tests with new features
- Update documentation as needed

## 10. CI/CD

### Continuous Integration
- Run tests on every push
- Lint and format code
- Build Docker images
- Run security scans

### Continuous Deployment
- Automate deployments to staging
- Require manual approval for production
- Implement blue-green deployments
- Monitor deployments

## 11. Monitoring & Logging

### Logging
- Use structured logging
- Include correlation IDs
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Rotate logs regularly

### Monitoring
- Track key metrics (response times, error rates, etc.)
- Set up alerts for critical issues
- Monitor resource usage
- Use distributed tracing

## 12. AI-Specific Guidelines

### Prompt Engineering
- Keep prompts clear and specific
- Include examples where appropriate
- Test prompts with different models
- Version control prompts

### Model Output Handling
- Validate model outputs
- Implement retry logic for transient failures
- Cache responses when appropriate
- Monitor for model drift

## 13. Accessibility

### Web Accessibility
- Follow WCAG 2.1 AA guidelines
- Use semantic HTML
- Ensure keyboard navigation
- Test with screen readers
- Provide text alternatives for non-text content

## 14. Internationalization

### i18n
- Use Unicode (UTF-8) for all text
- Externalize all user-facing strings
- Support right-to-left (RTL) languages
- Test with different locales

## 15. Compliance

### Data Protection
- Comply with GDPR and CCPA
- Implement data retention policies
- Encrypt sensitive data at rest and in transit
- Document data flows

### Security Audits
- Perform regular security audits
- Keep dependencies up to date
- Use Dependabot for dependency updates
- Have an incident response plan

## 16. Code Quality

### Static Analysis
- Use linters (flake8, ESLint)
- Run static type checking (mypy, TypeScript)
- Enforce code style with formatters (Black, Prettier)
- Use security scanning tools

### Code Review Guidelines
- Check for security vulnerabilities
- Verify test coverage
- Ensure documentation is updated
- Consider performance implications
- Look for code smells and technical debt

## 17. Onboarding

### New Developers
- Document local setup
- Provide a checklist for first contributions
- Assign a mentor for the first month
- Schedule regular check-ins

### Knowledge Sharing
- Document architectural decisions (ADR)
- Conduct regular knowledge sharing sessions
- Maintain a project wiki
- Document tribal knowledge

## 18. Incident Management

### Incident Response
- Document incident response procedures
- Have a rollback plan
- Conduct post-mortems for major incidents
- Track action items from incidents

### Communication
- Notify stakeholders of incidents
- Provide regular updates during incidents
- Document root cause analysis
- Share learnings with the team

## 19. Performance Optimization

### Frontend
- Optimize images and assets
- Implement lazy loading
- Use web workers for CPU-intensive tasks
- Minimize re-renders

### Backend
- Implement caching strategies
- Optimize database queries
- Use connection pooling
- Monitor and optimize memory usage

## 20. Scalability

### Horizontal Scaling
- Design stateless services
- Use distributed caching
- Implement database sharding if needed
- Use message queues for async processing

### Load Testing
- Perform regular load testing
- Identify and fix bottlenecks
- Set up auto-scaling rules
- Monitor performance under load

## 21. Technical Debt

### Management
- Track technical debt in the backlog
- Allocate time for addressing technical debt
- Document known issues
- Prioritize high-impact debt

### Refactoring
- Refactor in small, incremental changes
- Write tests before refactoring
- Verify functionality after refactoring
- Document architectural changes

## 22. Team Collaboration

### Communication
- Use asynchronous communication by default
- Document decisions and discussions
- Be respectful and inclusive
- Provide constructive feedback

### Pair Programming
- Rotate pairs regularly
- Set clear goals for pairing sessions
- Share knowledge and techniques
- Take breaks as needed

## 23. Continuous Improvement

### Retrospectives
- Hold regular retrospectives
- Document action items
- Follow up on previous action items
- Celebrate successes

### Learning & Development
- Allocate time for learning
- Share learnings with the team
- Attend conferences and workshops
- Contribute to open source

## 24. Accessibility & Inclusivity

### Team Culture
- Foster an inclusive environment
- Be mindful of different time zones
- Accommodate different working styles
- Encourage diverse perspectives

### Product Development
- Consider diverse user needs
- Test with diverse user groups
- Address accessibility from the start
- Follow inclusive design principles

## 25. Exit Criteria

### Feature Completion
- All acceptance criteria met
- Tests written and passing
- Documentation updated
- Stakeholder sign-off

### Definition of Done
- Code reviewed and approved
- Tests passing in CI
- Performance benchmarks met
- Deployed to production
- Monitoring in place
