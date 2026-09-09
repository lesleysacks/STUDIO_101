import { initNavigation } from './modules/navigation.js';
import { initAnimations } from './modules/animations.js';
import { initFormValidation } from './modules/form_validation.js';

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initAnimations();
    initFormValidation();
});
