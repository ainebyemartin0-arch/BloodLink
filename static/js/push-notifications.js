const VAPID_PUBLIC_KEY = document.querySelector(
    'meta[name="vapid-public-key"]'
)?.content;

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function registerServiceWorker() {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.log('Push notifications not supported');
        return null;
    }
    
    try {
        const registration = await navigator.serviceWorker.register(
            '/static/js/service-worker.js',
            { scope: '/' }
        );
        console.log('BloodLink Service Worker registered');
        return registration;
    } catch (error) {
        console.error('Service Worker registration failed:', error);
        return null;
    }
}

async function subscribeToPushNotifications(csrfToken) {
    const registration = await registerServiceWorker();
    if (!registration) return;
    
    try {
        const permission = await Notification.requestPermission();
        
        if (permission !== 'granted') {
            console.log('Notification permission denied');
            showPushStatus('blocked');
            return;
        }
        
        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
        });
        
        const subscriptionData = subscription.toJSON();
        
        const response = await fetch('/notifications/push/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                endpoint: subscriptionData.endpoint,
                p256dh: subscriptionData.keys.p256dh,
                auth: subscriptionData.keys.auth,
            })
        });
        
        if (response.ok) {
            console.log('Push subscription saved successfully');
            showPushStatus('subscribed');
        }
        
    } catch (error) {
        console.error('Push subscription failed:', error);
    }
}

function showPushStatus(status) {
    const btn = document.getElementById('pushSubscribeBtn');
    if (!btn) return;
    
    if (status === 'subscribed') {
        btn.innerHTML = '🔔 Notifications ON';
        btn.classList.remove('btn-bl-outline');
        btn.classList.add('btn-bl-green');
        btn.disabled = true;
    } else if (status === 'blocked') {
        btn.innerHTML = '🔕 Notifications Blocked';
        btn.classList.add('btn-bl-ghost');
        btn.disabled = true;
    }
}

async function checkExistingSubscription() {
    if (!('serviceWorker' in navigator)) return;
    
    const registration = await navigator.serviceWorker.getRegistration();
    if (!registration) return;
    
    const subscription = await registration.pushManager.getSubscription();
    if (subscription) {
        showPushStatus('subscribed');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    checkExistingSubscription();
    
    const btn = document.getElementById('pushSubscribeBtn');
    if (btn) {
        const csrfToken = document.querySelector(
            '[name=csrfmiddlewaretoken]'
        )?.value || 
        document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
        
        btn.addEventListener('click', function() {
            subscribeToPushNotifications(csrfToken);
        });
    }
});
