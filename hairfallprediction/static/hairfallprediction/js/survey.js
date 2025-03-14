
        const questions = [
            {
                title: "What is your gender?",
                description: "Select your gender identity",
                type: "select",
                options: ["Female", "Male", "Other"],
                icon: "fas fa-venus-mars",
                background: "/api/placeholder/800/600"
            },
            {
                title: "What is your age?",
                description: "Enter your current age",
                type: "number",
                placeholder: "Enter age",
                icon: "fas fa-user-clock",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Hairline Pattern",
                description: "Select your current hairline pattern",
                type: "select",
                options: ["Normal", "Receding", "Type 2", "Type 3", "Type 4", "Type 5"],
                icon: "fas fa-user",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Hair Fall Rate",
                description: "Daily hair fall count",
                type: "number",
                placeholder: "Strands per day",
                icon: "fas fa-chart-line",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Nutrition Level",
                description: "Rate your nutrition from 1-10",
                type: "number",
                placeholder: "1-10",
                icon: "fas fa-apple-whole",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Chemical Product Usage",
                description: "Rate your chemical product usage",
                type: "select",
                options: ["No Usage", "Light Usage", "Moderate Usage", "Heavy Usage"],
                icon: "fas fa-spray-can",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Family History",
                description: "Family history of hair loss",
                type: "select",
                options: ["No History", "Some History", "Strong History"],
                icon: "fas fa-users",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Past Chronic Illness",
                description: "History of chronic illness",
                type: "select",
                options: ["None", "Yes", "Severe"],
                icon: "fas fa-hospital",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Sleep Disturbance",
                description: "Rate your sleep quality",
                type: "select",
                options: ["No Issues", "Some Issues", "Severe Issues"],
                icon: "fas fa-moon",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Water Quality",
                description: "Rate your water quality",
                type: "select",
                options: ["Good", "Poor", "Very Poor"],
                icon: "fas fa-water",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Stress Levels",
                description: "Rate your stress levels",
                type: "select",
                options: ["Low", "Medium", "High", "Extreme"],
                icon: "fas fa-brain",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Food Habits",
                description: "Rate your eating habits",
                type: "select",
                options: ["Healthy", "Moderate", "Unhealthy", "Very Unhealthy"],
                icon: "fas fa-utensils",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Hormonal Changes",
                description: "Any hormonal imbalances?",
                type: "select",
                options: ["No", "Yes"],
                icon: "fas fa-chart-bar",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Hair Care Habits",
                description: "Rate your hair care routine",
                type: "select",
                options: ["Good", "Poor"],
                icon: "fas fa-pump-soap",
                background: "/api/placeholder/800/600"
            },
            {
                title: "Smoking Habits",
                description: "Do you smoke?",
                type: "select",
                options: ["No", "Yes"],
                icon: "fas fa-smoking",
                background: "/api/placeholder/800/600"
            }
        ];

        // Rest of the JavaScript remains the same as in your original code
        let currentSlide = 0;
        const sliderContainer = document.querySelector('.slider-container');
        const progressBar = document.querySelector('.progress-bar');

        // Create slides (same as your original code)
        questions.forEach((question, index) => {
            const slide = document.createElement('div');
            slide.className = `slide ${index === 0 ? 'active' : ''}`;

            const visualSection = document.createElement('div');
            visualSection.className = 'visual-section';

            const iconContainer = document.createElement('div');
            iconContainer.className = 'icon-container';
            iconContainer.innerHTML = `<i class="${question.icon}"></i>`;

            const imageContainer = document.createElement('div');
            imageContainer.className = 'image-container';
            imageContainer.innerHTML = `<img src="${question.background}" alt="Question illustration">`;

            visualSection.appendChild(iconContainer);
            visualSection.appendChild(imageContainer);

            const questionSection = document.createElement('div');
            questionSection.className = 'question-section';

            const questionContainer = document.createElement('div');
            questionContainer.className = 'question-container';

            const title = document.createElement('h2');
            title.textContent = question.title;

            const description = document.createElement('div');
            description.className = 'description';
            description.textContent = question.description;

            const inputContainer = document.createElement('div');
            inputContainer.className = 'input-container';

            if (question.type === 'select') {
                const select = document.createElement('select');
                question.options.forEach((option, i) => {
                    const optionElement = document.createElement('option');
                    optionElement.value = i;
                    optionElement.textContent = option;
                    select.appendChild(optionElement);
                });
                inputContainer.appendChild(select);
            } else {
                const input = document.createElement('input');
                input.type = 'number';
                input.placeholder = question.placeholder;
                inputContainer.appendChild(input);
            }

            const navigation = document.createElement('div');
            navigation.className = 'navigation';

            if (index > 0) {
                const prevButton = document.createElement('button');
                prevButton.textContent = 'Previous';
                prevButton.onclick = () => navigateSlide(-1);
                navigation.appendChild(prevButton);
            }

            if (index < questions.length - 1) {
                const nextButton = document.createElement('button');
                nextButton.textContent = 'Next';
                nextButton.onclick = () => navigateSlide(1);
                navigation.appendChild(nextButton);
            } else {
                const submitButton = document.createElement('button');
                submitButton.textContent = 'Submit';
                submitButton.onclick = handleSubmit;
                navigation.appendChild(submitButton);
            }

            questionContainer.appendChild(title);
            questionContainer.appendChild(description);
            questionContainer.appendChild(inputContainer);
            questionContainer.appendChild(navigation);
            questionSection.appendChild(questionContainer);

            slide.appendChild(visualSection);
            slide.appendChild(questionSection);
            sliderContainer.appendChild(slide);
        });

        function navigateSlide(direction) {
            const slides = document.querySelectorAll('.slide');
            slides[currentSlide].classList.remove('active');
            currentSlide += direction;
            slides[currentSlide].classList.add('active');
            updateProgressBar();
        }

        function updateProgressBar() {
            const progress = ((currentSlide + 1) / questions.length) * 100;
            progressBar.style.width = `${progress}%`;
        }

        function handleSubmit() {
            const answers = {};
            const inputs = document.querySelectorAll('input, select');
            inputs.forEach((input, index) => {
                answers[questions[index].title] = input.value;
            });
            console.log('Submitted answers:', answers);
        }

        updateProgressBar();