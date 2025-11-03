class LoginManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupFormToggle();
        this.setupLoginForm();
        this.setupSignupForm();
    }

    setupFormToggle() {
        const showSignupBtn = document.getElementById('show-signup');
        const showLoginBtn = document.getElementById('show-login');
        const loginContainer = document.getElementById('login-form').parentElement;
        const signupContainer = document.getElementById('signup-container');

        showSignupBtn.addEventListener('click', () => {
            loginContainer.style.display = 'none';
            signupContainer.style.display = 'block';
        });

        showLoginBtn.addEventListener('click', () => {
            signupContainer.style.display = 'none';
            loginContainer.style.display = 'block';
        });
    }

    setupLoginForm() {
        const form = document.getElementById('login-form');
        const errorDiv = document.getElementById('login-error');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;
            const remember = document.getElementById('remember').checked;

            // Hide previous errors
            errorDiv.style.display = 'none';

            // Show loading state
            this.setButtonLoading('login-btn', true);

            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password, remember })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Store user data in localStorage
                    localStorage.setItem('currentUser', JSON.stringify(data.user));

                    // Successful login - redirect to dashboard
                    window.location.href = '/dashboard';
                } else {
                    // Show error message
                    this.showError('login-error', data.message || 'Login failed');
                }
            } catch (error) {
                this.showError('login-error', 'Connection error. Please try again.');
            } finally {
                this.setButtonLoading('login-btn', false);
            }
        });
    }

    setupSignupForm() {
        const form = document.getElementById('signup-form');
        const errorDiv = document.getElementById('signup-error');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('signup-username').value.trim();
            const email = document.getElementById('signup-email').value.trim();
            const password = document.getElementById('signup-password').value;

            // Validate password length
            if (password.length < 6) {
                this.showError('signup-error', 'Password must be at least 6 characters');
                return;
            }

            // Hide previous errors
            errorDiv.style.display = 'none';

            // Show loading state
            this.setButtonLoading('signup-btn', true);

            try {
                const response = await fetch('/auth/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    // Store user data in localStorage
                    localStorage.setItem('currentUser', JSON.stringify(data.user));

                    // Successful signup - redirect to dashboard
                    window.location.href = '/dashboard';
                } else {
                    // Show error message
                    this.showError('signup-error', data.message || 'Signup failed');
                }
            } catch (error) {
                this.showError('signup-error', 'Connection error. Please try again.');
            } finally {
                this.setButtonLoading('signup-btn', false);
            }
        });
    }

    showError(errorId, message) {
        const errorDiv = document.getElementById(errorId);
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }

    setButtonLoading(buttonId, loading) {
        const button = document.getElementById(buttonId);
        const text = document.getElementById(buttonId + '-text');
        const loader = document.getElementById(buttonId.replace('-btn', '-loader'));

        if (loading) {
            button.disabled = true;
            text.style.display = 'none';
            loader.style.display = 'block';
        } else {
            button.disabled = false;
            text.style.display = 'block';
            loader.style.display = 'none';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new LoginManager();
});
