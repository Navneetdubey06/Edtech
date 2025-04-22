// Main script file for the learning portal

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Lesson completion tracking
    const markAsCompleteBtn = document.getElementById('markAsComplete');
    if (markAsCompleteBtn) {
        markAsCompleteBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const form = document.getElementById('completeForm');
            if (form) {
                form.submit();
            }
        });
    }
    
    // Quiz form handling - show/hide option fields based on question type
    const questionTypeSelect = document.getElementById('question_type');
    if (questionTypeSelect) {
        const optionsField = document.getElementById('options-group');
        const correctAnswerHelp = document.getElementById('correct-answer-help');
        
        function updateQuestionTypeFields() {
            const selectedType = questionTypeSelect.value;
            
            if (selectedType === 'mcq') {
                if (optionsField) optionsField.style.display = 'block';
                if (correctAnswerHelp) correctAnswerHelp.textContent = 'Enter the index of the correct option (starting from 0)';
            } else if (selectedType === 'true_false') {
                if (optionsField) optionsField.style.display = 'none';
                if (correctAnswerHelp) correctAnswerHelp.textContent = 'Enter "true" or "false"';
            } else if (selectedType === 'short_answer') {
                if (optionsField) optionsField.style.display = 'none';
                if (correctAnswerHelp) correctAnswerHelp.textContent = 'Enter the expected answer';
            }
        }
        
        questionTypeSelect.addEventListener('change', updateQuestionTypeFields);
        
        // Initial call to set fields properly when page loads
        updateQuestionTypeFields();
    }
    
    // Time tracking for lessons
    const lessonContent = document.getElementById('lessonContent');
    if (lessonContent) {
        let startTime = new Date();
        let timeSpent = 0;
        
        // Every 30 seconds, update the time spent
        setInterval(function() {
            // Only count time if the page is visible
            if (document.visibilityState === 'visible') {
                const currentTime = new Date();
                timeSpent += (currentTime - startTime) / 1000; // Convert to seconds
                startTime = currentTime;
                
                // You might want to send this to the server periodically
                // For demonstration, we'll just log it
                console.log('Time spent on lesson: ' + Math.round(timeSpent) + ' seconds');
            }
        }, 30000); // 30 seconds
        
        // Update startTime when the page becomes visible again
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'visible') {
                startTime = new Date();
            }
        });
    }
    
    // Course search functionality
    const searchInput = document.getElementById('courseSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const courseCards = document.querySelectorAll('.course-card');
            
            courseCards.forEach(function(card) {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const description = card.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Countdown timer for quizzes
    const quizTimer = document.getElementById('quizTimer');
    if (quizTimer) {
        const duration = parseInt(quizTimer.getAttribute('data-duration') || '0');
        if (duration > 0) {
            let timeLeft = duration * 60; // Convert to seconds
            
            const timerInterval = setInterval(function() {
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                
                quizTimer.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
                
                if (--timeLeft < 0) {
                    clearInterval(timerInterval);
                    quizTimer.textContent = 'Time\'s up!';
                    // Auto submit the form
                    document.querySelector('form').submit();
                }
            }, 1000);
        }
    }
    
    // Admin course management - sortable chapters and lessons
    const chapterList = document.getElementById('chapterList');
    if (chapterList) {
        // Here you would typically initialize a drag-and-drop library
        // For this example, we'll just show/hide the lessons
        const toggleButtons = document.querySelectorAll('.toggle-lessons');
        toggleButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                const chapterId = this.getAttribute('data-chapter-id');
                const lessonList = document.getElementById('lessons-' + chapterId);
                
                if (lessonList) {
                    if (lessonList.style.display === 'none') {
                        lessonList.style.display = 'block';
                        this.textContent = 'Hide Lessons';
                    } else {
                        lessonList.style.display = 'none';
                        this.textContent = 'Show Lessons';
                    }
                }
            });
        });
    }
    
    // Payment form validation
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            const termsCheckbox = document.getElementById('terms');
            if (!termsCheckbox.checked) {
                e.preventDefault();
                alert('Please agree to the terms and conditions to proceed with payment.');
            }
        });
    }
});
