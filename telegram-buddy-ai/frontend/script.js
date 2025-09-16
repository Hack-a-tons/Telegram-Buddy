async function submitMessage() {
    const content = document.getElementById('messageInput').value;
    const projectId = document.getElementById('projectInput').value || 'default';
    
    if (!content.trim()) {
        alert('Please enter a message');
        return;
    }
    
    try {
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `content=${encodeURIComponent(content)}&project_id=${encodeURIComponent(projectId)}`
        });
        
        const result = await response.json();
        
        if (result.processed) {
            alert(`Message processed! Found ${result.action_items_found} action items.`);
            document.getElementById('messageInput').value = '';
        }
    } catch (error) {
        alert('Error submitting message: ' + error.message);
    }
}

async function askQuestion() {
    const question = document.getElementById('questionInput').value;
    const projectId = document.getElementById('projectInput').value || 'default';
    
    if (!question.trim()) {
        alert('Please enter a question');
        return;
    }
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                project_id: projectId
            })
        });
        
        const result = await response.json();
        
        document.getElementById('answerOutput').innerHTML = `
            <strong>Answer:</strong><br>
            ${result.answer}<br><br>
            <small>Confidence: ${(result.confidence * 100).toFixed(1)}%</small>
        `;
        
        document.getElementById('questionInput').value = '';
    } catch (error) {
        document.getElementById('answerOutput').innerHTML = 'Error: ' + error.message;
    }
}

async function loadActions() {
    const projectId = document.getElementById('projectInput').value || 'default';
    
    try {
        const response = await fetch(`/api/actions/${projectId}`);
        const actions = await response.json();
        
        const output = document.getElementById('actionsOutput');
        
        if (actions.length === 0) {
            output.innerHTML = 'No unresolved action items found.';
        } else {
            output.innerHTML = actions.map(action => `
                <div class="action-item">
                    <strong>${action.description}</strong><br>
                    <small>Mentioned: ${new Date(action.mentioned_at).toLocaleString()}</small>
                    ${action.assigned_to ? `<br><small>Assigned to: @${action.assigned_to}</small>` : ''}
                </div>
            `).join('');
        }
    } catch (error) {
        document.getElementById('actionsOutput').innerHTML = 'Error: ' + error.message;
    }
}

async function loadContext() {
    const projectId = document.getElementById('projectInput').value || 'default';
    
    try {
        const response = await fetch(`/api/context/${projectId}`);
        const context = await response.json();
        
        const output = document.getElementById('contextOutput');
        
        if (context.messages.length === 0) {
            output.innerHTML = 'No messages in context yet.';
        } else {
            output.innerHTML = `
                <strong>Project: ${context.project_id}</strong><br>
                <strong>Messages: ${context.messages.length}</strong><br>
                <strong>Last Updated: ${new Date(context.last_updated).toLocaleString()}</strong><br><br>
                <strong>Recent Messages:</strong><br>
                ${context.messages.slice(-5).map(msg => `
                    <div class="message">
                        <small>${new Date(msg.timestamp).toLocaleString()}</small><br>
                        ${msg.content}
                    </div>
                `).join('')}
            `;
        }
    } catch (error) {
        document.getElementById('contextOutput').innerHTML = 'Error: ' + error.message;
    }
}
