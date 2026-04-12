self.addEventListener('push', function(event) {
    let data = {};
    
    if (event.data) {
        try {
            data = event.data.json();
        } catch(e) {
            data = {
                title: '🩸 BloodLink Alert',
                body: event.data.text(),
                url: '/donor/dashboard/'
            };
        }
    }
    
    const options = {
        body: data.body || 'New notification from BloodLink',
        icon: data.icon || '/static/images/bloodlink-icon.png',
        badge: data.badge || '/static/images/bloodlink-badge.png',
        vibrate: [200, 100, 200, 100, 200],
        requireInteraction: true,
        actions: [
            {
                action: 'respond',
                title: '✅ I Can Donate',
            },
            {
                action: 'dismiss',
                title: '❌ Not Available',
            }
        ],
        data: {
            url: data.url || '/donor/dashboard/',
            dateOfArrival: Date.now(),
        },
        tag: 'bloodlink-emergency',
        renotify: true,
    };
    
    event.waitUntil(
        self.registration.showNotification(
            data.title || '🩸 BloodLink Emergency Alert',
            options
        )
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    const urlToOpen = event.notification.data.url || '/donor/dashboard/';
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(function(windowClients) {
                for (let client of windowClients) {
                    if (client.url.includes(self.location.origin) && 
                        'focus' in client) {
                        client.navigate(urlToOpen);
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

self.addEventListener('notificationclose', function(event) {
    console.log('BloodLink notification closed');
});
