package com.todoapp.application.service;

import com.sendgrid.Method;
import com.sendgrid.Request;
import com.sendgrid.Response;
import com.sendgrid.SendGrid;
import com.sendgrid.helpers.mail.Mail;
import com.sendgrid.helpers.mail.objects.Content;
import com.sendgrid.helpers.mail.objects.Email;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.io.IOException;

@Slf4j
@Service
public class EmailService {

    private final SendGrid sendGrid;
    private final String fromEmail;
    private final String fromName;
    private final boolean enabled;

    public EmailService(
            @Value("${sendgrid.api-key:}") String apiKey,
            @Value("${sendgrid.from-email:noreply@todoapp.com}") String fromEmail,
            @Value("${sendgrid.from-name:Todo App}") String fromName,
            @Value("${sendgrid.enabled:false}") boolean enabled) {
        this.sendGrid = new SendGrid(apiKey);
        this.fromEmail = fromEmail;
        this.fromName = fromName;
        this.enabled = enabled;
    }

    @Async
    public void sendEmail(String toEmail, String subject, String htmlContent) {
        if (!enabled) {
            log.info("Email sending disabled. Would send to: {} with subject: {}", toEmail, subject);
            return;
        }

        try {
            Email from = new Email(fromEmail, fromName);
            Email to = new Email(toEmail);
            Content content = new Content("text/html", htmlContent);
            Mail mail = new Mail(from, subject, to, content);

            Request request = new Request();
            request.setMethod(Method.POST);
            request.setEndpoint("mail/send");
            request.setBody(mail.build());

            Response response = sendGrid.api(request);

            if (response.getStatusCode() >= 200 && response.getStatusCode() < 300) {
                log.info("Email sent successfully to: {}", toEmail);
            } else {
                log.error("Failed to send email. Status: {}, Body: {}", 
                    response.getStatusCode(), response.getBody());
            }
        } catch (IOException e) {
            log.error("Error sending email to: " + toEmail, e);
        }
    }
}
