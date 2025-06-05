// Support Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
  // FAQ Accordion
  const faqItems = document.querySelectorAll('.faq-item');
  
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');
    const icon = question.querySelector('i');
    
    question.addEventListener('click', () => {
      // Toggle active class on the clicked item
      const isActive = item.classList.contains('active');
      
      // Close all items
      faqItems.forEach(faqItem => {
        faqItem.classList.remove('active');
        faqItem.querySelector('.faq-answer').style.maxHeight = '0';
        faqItem.querySelector('.faq-question i').className = 'fas fa-chevron-down';
      });
      
      // Open clicked item if it wasn't active
      if (!isActive) {
        item.classList.add('active');
        answer.style.maxHeight = answer.scrollHeight + 'px';
        icon.className = 'fas fa-chevron-up';
      }
    });
  });
  
  // Support Form Submission
  const supportForm = document.getElementById('support-form');
  
  if (supportForm) {
    supportForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Get the submit button
      const submitBtn = supportForm.querySelector('button[type="submit"]');
      const originalBtnText = submitBtn.innerHTML;
      
      // Set loading state
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
      
      // Simple form validation
      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const subject = document.getElementById('subject').value;
      const message = document.getElementById('message').value.trim();
      
      if (!name || !email || !subject || !message) {
        alert('Please fill in all required fields');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
        return;
      }
      
      // Here you would typically send this data to your server
      console.log('Form submitted:', { name, email, subject, message });
      
      // Simulate API call
      setTimeout(() => {
        // Show success message
        alert('Thank you for contacting us! We will get back to you soon.');
        
        // Reset the form and button state
        supportForm.reset();
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }, 1000);
    });
  }
  
  // Initialize any open FAQ items
  const activeItem = document.querySelector('.faq-item.active');
  if (activeItem) {
    const answer = activeItem.querySelector('.faq-answer');
    answer.style.maxHeight = answer.scrollHeight + 'px';
  }
});
