/**
 * Profile page logic for khappha.online
 * Handles profile viewing, editing, avatar upload, and password change
 */

let isEditMode = false;
let originalFormData = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeProfile();
    setupEventListeners();
    loadUserProfile();
});

function initializeProfile() {
    // Store original form data
    const form = document.getElementById('profileForm');
    if (form) {
        const formData = new FormData(form);
        formData.forEach((value, key) => {
            originalFormData[key] = value;
        });
    }
}

function setupEventListeners() {
    // Edit mode button
    const editModeBtn = document.getElementById('editModeBtn');
    if (editModeBtn) {
        editModeBtn.addEventListener('click', toggleEditMode);
    }
    
    // Cancel edit button
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', cancelEdit);
    }
    
    // Save profile button
    const saveProfileBtn = document.getElementById('saveProfileBtn');
    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', saveProfile);
    }
    
    // Avatar upload
    const avatarInput = document.getElementById('avatarInput');
    if (avatarInput) {
        avatarInput.addEventListener('change', handleAvatarUpload);
    }
    
    // Change password button
    const changePasswordBtn = document.getElementById('changePasswordBtn');
    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', openPasswordModal);
    }
    
    // Delete account button
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', confirmDeleteAccount);
    }
    
    // Password modal buttons
    const closePasswordModal = document.getElementById('closePasswordModal');
    const cancelPasswordBtn = document.getElementById('cancelPasswordBtn');
    if (closePasswordModal) {
        closePasswordModal.addEventListener('click', () => hideModal('passwordModal'));
    }
    if (cancelPasswordBtn) {
        cancelPasswordBtn.addEventListener('click', () => hideModal('passwordModal'));
    }
    
    // Change password form
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', handlePasswordChange);
    }
}

function toggleEditMode() {
    isEditMode = !isEditMode;
    
    const editModeBtn = document.getElementById('editModeBtn');
    const editActions = document.getElementById('editActions');
    const formInputs = document.querySelectorAll('.form-input');
    
    if (isEditMode) {
        // Enable edit mode
        editModeBtn.innerHTML = `
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            <span>Hủy</span>
        `;
        editModeBtn.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        editModeBtn.classList.add('bg-gray-600', 'hover:bg-gray-700');
        
        editActions.classList.remove('hidden');
        editActions.classList.add('flex');
        
        formInputs.forEach(input => {
            // Don't enable email (unique field)
            if (input.id !== 'inputEmail') {
                input.disabled = false;
            }
        });
    } else {
        cancelEdit();
    }
}

function cancelEdit() {
    isEditMode = false;
    
    const editModeBtn = document.getElementById('editModeBtn');
    const editActions = document.getElementById('editActions');
    const formInputs = document.querySelectorAll('.form-input');
    
    // Reset button
    editModeBtn.innerHTML = `
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
        <span>Chỉnh sửa</span>
    `;
    editModeBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
    editModeBtn.classList.remove('bg-gray-600', 'hover:bg-gray-700');
    
    editActions.classList.add('hidden');
    editActions.classList.remove('flex');
    
    // Disable inputs and restore original values
    formInputs.forEach(input => {
        input.disabled = true;
        const fieldName = input.name;
        if (originalFormData[fieldName] !== undefined) {
            input.value = originalFormData[fieldName];
        }
    });
}

async function saveProfile() {
    try {
        const form = document.getElementById('profileForm');
        const formData = new FormData(form);
        
        const profileData = {
            full_name: formData.get('full_name'),
            username: formData.get('username'),
            bio: formData.get('bio'),
            phone: formData.get('phone'),
            address: formData.get('address'),
            date_of_birth: formData.get('date_of_birth'),
            travel_preferences: {
                travel_type: document.getElementById('inputTravelType').value,
                budget_range: document.getElementById('inputBudgetRange').value
            }
        };
        
        const response = await fetch('/api/profile', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Cập nhật thông tin thành công!', 'success');
            
            // Update display
            updateDisplayInfo(data.user);
            
            // Store new original data
            originalFormData = {};
            formData.forEach((value, key) => {
                originalFormData[key] = value;
            });
            
            // Exit edit mode
            cancelEdit();
        } else {
            showToast(data.error || 'Không thể cập nhật thông tin', 'error');
        }
    } catch (error) {
        console.error('Error saving profile:', error);
        showToast('Lỗi hệ thống, vui lòng thử lại', 'error');
    }
}

function updateDisplayInfo(user) {
    // Update header info
    if (document.getElementById('displayFullName')) {
        document.getElementById('displayFullName').textContent = user.full_name || user.username || 'Người dùng';
    }
    if (document.getElementById('displayUsername')) {
        document.getElementById('displayUsername').textContent = `@${user.username || 'user'}`;
    }
    if (document.getElementById('displayEmail')) {
        document.getElementById('displayEmail').textContent = user.email || 'Chưa có email';
    }
    
    // Update avatar if changed
    if (user.avatar_url && document.getElementById('profileAvatar')) {
        document.getElementById('profileAvatar').src = user.avatar_url;
    }
}

async function handleAvatarUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showToast('Kích thước file không được vượt quá 5MB', 'error');
        return;
    }
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showToast('Vui lòng chọn file ảnh', 'error');
        return;
    }
    
    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('profileAvatar').src = e.target.result;
    };
    reader.readAsDataURL(file);
    
    // Upload to server
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/profile/avatar', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Cập nhật ảnh đại diện thành công!', 'success');
            document.getElementById('profileAvatar').src = data.avatar_url;
        } else {
            showToast(data.error || 'Không thể tải lên ảnh', 'error');
        }
    } catch (error) {
        console.error('Error uploading avatar:', error);
        showToast('Lỗi tải lên ảnh, vui lòng thử lại', 'error');
    }
}

function openPasswordModal() {
    showModal('passwordModal');
    // Clear form
    document.getElementById('changePasswordForm').reset();
}

async function handlePasswordChange(event) {
    event.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validate
    if (!currentPassword || !newPassword || !confirmPassword) {
        showToast('Vui lòng nhập đầy đủ thông tin', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showToast('Mật khẩu xác nhận không khớp', 'error');
        return;
    }
    
    if (newPassword.length < 8) {
        showToast('Mật khẩu phải có ít nhất 8 ký tự', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/profile/password', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Đổi mật khẩu thành công!', 'success');
            hideModal('passwordModal');
            document.getElementById('changePasswordForm').reset();
        } else {
            showToast(data.error || 'Không thể đổi mật khẩu', 'error');
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showToast('Lỗi hệ thống, vui lòng thử lại', 'error');
    }
}

function confirmDeleteAccount() {
    if (confirm('⚠️ BẠN CÓ CHẮC CHẮN MUỐN XÓA TÀI KHOẢN?\n\nHành động này không thể hoàn tác. Tất cả dữ liệu của bạn sẽ bị xóa vĩnh viễn.')) {
        const password = prompt('Vui lòng nhập mật khẩu để xác nhận:');
        if (password) {
            deleteAccount(password);
        }
    }
}

async function deleteAccount(password) {
    try {
        const response = await fetch('/api/profile', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Tài khoản đã được xóa', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showToast(data.error || 'Không thể xóa tài khoản', 'error');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        showToast('Lỗi hệ thống, vui lòng thử lại', 'error');
    }
}

async function loadUserProfile() {
    try {
        const response = await fetch('/api/profile');
        const data = await response.json();
        
        if (data.success && data.user) {
            // Update form with user data
            const user = data.user;
            
            if (user.travel_preferences) {
                if (user.travel_preferences.travel_type) {
                    document.getElementById('inputTravelType').value = user.travel_preferences.travel_type;
                }
                if (user.travel_preferences.budget_range) {
                    document.getElementById('inputBudgetRange').value = user.travel_preferences.budget_range;
                }
            }
            
            // Update stats if provided
            if (data.stats) {
                updateStats(data.stats);
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

function updateStats(stats) {
    if (document.getElementById('statPlans')) {
        document.getElementById('statPlans').textContent = stats.total_plans || 0;
    }
    if (document.getElementById('statCompleted')) {
        document.getElementById('statCompleted').textContent = stats.completed_plans || 0;
    }
    if (document.getElementById('statDestinations')) {
        document.getElementById('statDestinations').textContent = stats.destinations || 0;
    }
    if (document.getElementById('statDays')) {
        document.getElementById('statDays').textContent = stats.total_days || 0;
    }
}

// Utility functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-[9999] px-6 py-3 rounded-lg shadow-lg text-white transform transition-all duration-300 translate-x-0`;
    
    if (type === 'success') {
        toast.classList.add('bg-green-500');
    } else if (type === 'error') {
        toast.classList.add('bg-red-500');
    } else {
        toast.classList.add('bg-blue-500');
    }
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(400px)';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}
