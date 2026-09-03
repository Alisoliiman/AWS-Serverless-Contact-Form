document.getElementById('contactForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent default page refresh on submit

    const submitBtn = document.getElementById('submitBtn');
    const responseMessage = document.getElementById('responseMessage');
    
    // 1. Check Honeypot field to prevent automated bot spam
    const honeypot = document.getElementById('website').value;
    if (honeypot !== "") {
        // Silent block for spam bots
        responseMessage.className = "response-message success";
        responseMessage.innerText = "تم إرسال رسالتك بنجاح!";
        responseMessage.style.display = "block";
        return;
    }

    // 2. Extract input values from form
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        subject: document.getElementById('subject').value,
        message: document.getElementById('message').value
    };

    // Update button UI state to sending mode
    submitBtn.disabled = true;
    submitBtn.innerText = "جاري الإرسال...";
    responseMessage.style.display = "none";

    try {
        // API Gateway endpoint URL
        const API_URL = "https://mhv27wvj96.execute-api.us-east-2.amazonaws.com/prod/contact";

        // Execute asynchronous HTTP POST request to API Gateway
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        // Parse response and verify status code (200 OK)
        if (response.ok) {
            responseMessage.className = "response-message success";
            responseMessage.innerText = "تم إرسال رسالتك بنجاح! سنترد عليك قريباً.";
            responseMessage.style.display = "block";
            document.getElementById('contactForm').reset(); // Reset form inputs
        } else {
            const errorData = await response.json().catch(() => ({}));
            console.error("API Error Response:", errorData);
            throw new Error("API Execution Failed");
        }
    } catch (error) {
        console.error("Submission Failure:", error);
        responseMessage.className = "response-message error";
        responseMessage.innerText = "تعذر إرسال الرسالة، يرجى المحاولة لاحقاً.";
        responseMessage.style.display = "block";
    } finally {
        // Restore submit button to initial state
        submitBtn.disabled = false;
        submitBtn.innerText = "إرسال الرسالة";
    }
});