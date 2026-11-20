CREATE DATABASE IF NOT EXISTS job_recommendation_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE job_recommendation_system;
CREATE TABLE IF NOT EXISTS users(user_id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(100) NOT NULL,email VARCHAR(150) NOT NULL UNIQUE,password_hash VARCHAR(255) NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS user_profiles(profile_id INT AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL UNIQUE,education VARCHAR(150),experience VARCHAR(50),interests TEXT,skills TEXT,updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS jobs(job_id INT AUTO_INCREMENT PRIMARY KEY,title VARCHAR(150) NOT NULL UNIQUE,category VARCHAR(100) NOT NULL,description TEXT,required_skills TEXT NOT NULL,education VARCHAR(150));
CREATE TABLE IF NOT EXISTS recommendations(recommendation_id INT AUTO_INCREMENT PRIMARY KEY,user_id INT NOT NULL,job_id INT NOT NULL,match_score DECIMAL(5,2) NOT NULL,input_skills TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE,FOREIGN KEY(job_id) REFERENCES jobs(job_id) ON DELETE CASCADE);
INSERT IGNORE INTO jobs(title,category,description,required_skills,education) VALUES
('Python Developer','Software Development','Build and maintain Python applications.','Python;SQL;Git;Flask;REST API','Computer Science or related'),
('Java Developer','Software Development','Develop backend applications using Java.','Java;OOP;SQL;Spring Boot;Git','Computer Science or related'),
('Frontend Developer','Web Development','Create responsive website interfaces.','HTML;CSS;JavaScript;React;Git','Any relevant degree or portfolio'),
('Backend Developer','Software Development','Build server-side services and APIs.','Python;Java;SQL;REST API;Git','Computer Science or related'),
('Full Stack Developer','Web Development','Work on frontend and backend systems.','HTML;CSS;JavaScript;Python;SQL','Computer Science or related'),
('Data Analyst','Data and Analytics','Analyze data and communicate insights.','Python;SQL;Excel;Pandas;Statistics','Statistics IT Business or related'),
('Data Scientist','Data and Analytics','Use statistics and ML to analyze data.','Python;SQL;Statistics;Machine Learning;Pandas','Computer Science Mathematics or Statistics'),
('Machine Learning Intern','Artificial Intelligence','Assist with data preparation and ML experiments.','Python;Machine Learning;NumPy;Pandas;Scikit-learn','Computer Science or related'),
('AI Engineer','Artificial Intelligence','Develop AI-powered software features.','Python;Machine Learning;Deep Learning;TensorFlow;Git','Computer Science or related'),
('Database Administrator','Database','Maintain databases and backups.','SQL;MySQL;Database Design;Linux;Backup','IT or Computer Science'),
('SQL Developer','Database','Write queries and database reports.','SQL;MySQL;Database Design;Excel','IT or Computer Science'),
('Cybersecurity Analyst','Cybersecurity','Monitor systems and investigate security alerts.','Networking;Linux;Cybersecurity;Python;Security Tools','IT or Cybersecurity'),
('Network Engineer','Networking','Configure and maintain computer networks.','Networking;TCP/IP;Linux;Troubleshooting','IT or Networking'),
('Cloud Support Associate','Cloud Computing','Support cloud infrastructure and services.','Linux;Networking;AWS;Python;Troubleshooting','IT or Computer Science'),
('DevOps Engineer','Cloud and DevOps','Support automation and deployment.','Linux;Git;Docker;CI/CD;Python','Computer Science or related'),
('UI UX Designer','Design','Design user-friendly digital experiences.','UI Design;UX Research;Figma;Wireframing;Prototyping','Design or portfolio'),
('Graphic Designer','Design','Create visual content and brand assets.','Graphic Design;Photoshop;Illustrator;Creativity','Design or portfolio'),
('Digital Marketing Executive','Marketing','Plan and measure online campaigns.','SEO;Social Media;Content Writing;Analytics;Communication','Marketing or any degree'),
('Content Writer','Content and Media','Create written content for digital platforms.','Content Writing;Research;Editing;Communication;SEO','Any degree or writing portfolio'),
('HR Assistant','Human Resources','Support recruitment and employee administration.','Communication;MS Office;Recruitment;Organization','HR Business or any degree'),
('Business Analyst','Business','Translate business needs into process and data insights.','Excel;SQL;Communication;Problem Solving;Documentation','Business IT or related'),
('Accountant','Finance','Maintain financial records and prepare reports.','Accounting;Excel;Tally;Financial Reporting;Attention to Detail','Commerce or Accounting'),
('Project Coordinator','Management','Coordinate schedules and project communication.','Communication;Planning;Excel;Documentation;Teamwork','Any relevant degree'),
('QA Tester','Software Testing','Test software and report defects.','Manual Testing;Test Cases;SQL;Bug Tracking;Communication','Computer Science or related'),
('Mobile App Developer','Mobile Development','Build applications for mobile devices.','Java;Kotlin;Flutter;Dart;REST API','Computer Science or related'),
('Python Automation Tester','Software Testing','Automate software tests using Python.','Python;Selenium;Testing;Git;SQL','Computer Science or related'),
('Research Assistant','Research','Support research data collection and analysis.','Research;Excel;Statistics;Writing;Data Analysis','Relevant undergraduate or postgraduate'),
('Technical Support Engineer','IT Support','Help users diagnose technical issues.','Troubleshooting;Networking;Windows;Communication;Linux','IT or related'),
('E-commerce Executive','Business','Support online store operations.','Excel;Communication;Analytics;Customer Service;Digital Marketing','Any degree'),
('Data Entry Operator','Administration','Enter and maintain structured records.','Typing;Excel;Attention to Detail;Data Management','Any degree');
