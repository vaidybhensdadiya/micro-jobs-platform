// frontend/script.js

const API_BASE = 'http://localhost:5000/api/v1';

// --- Utility Functions ---
function getAuthHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

function handleApiError(response, errorData) {
    const msg = errorData.message || 'An error occurred';
    throw new Error(msg);
}

function showFormError(msg, formId = 'errorMsg') {
    const errorDiv = document.getElementById(formId);
    if (errorDiv) {
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
    } else {
        alert(msg);
    }
}

function logout() {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
    window.location.href = 'index.html';
}

function checkAuth() {
    if (!localStorage.getItem('jwt_token')) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// --- Auth Handling ---
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('registered') === 'true') {
            const errorDiv = document.getElementById('errorMsg');
            errorDiv.textContent = 'Account created successfully! Please login.';
            errorDiv.className = 'bg-green-500/10 border border-green-500 text-green-500 p-3 rounded-lg text-sm mb-4 block';
        }

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const res = await fetch(`${API_BASE}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();

                if (!res.ok) handleApiError(res, data);

                localStorage.setItem('jwt_token', data.access_token);
                localStorage.setItem('user_role', data.role);
                localStorage.setItem('user_name', data.name);

                window.location.href = 'dashboard.html';
            } catch (err) {
                showFormError(err.message);
            }
        });
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const role = document.querySelector('input[name="role"]:checked').value;

            try {
                const res = await fetch(`${API_BASE}/auth/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password, role })
                });
                const data = await res.json();

                if (!res.ok) handleApiError(res, data);

                // On success, redirect to login
                window.location.href = 'login.html?registered=true';
            } catch (err) {
                showFormError(err.message);
            }
        });
    }
});

// Auto-protect dashboard
if (window.location.pathname.includes('dashboard.html')) {
    checkAuth();
}

