class WebAppService {
  constructor() {
    this.webApp = null;
    this.isReady = false;
    this.initPromise = null;
  }

  init() {
    if (this.initPromise) {
      return this.initPromise;
    }

    this.initPromise = new Promise((resolve, reject) => {
      if (typeof window === 'undefined') {
        reject(new Error('Window is not defined'));
        return;
      }

      if (!window.WebApp) {
        const checkWebApp = setInterval(() => {
          if (window.WebApp) {
            clearInterval(checkWebApp);
            this.webApp = window.WebApp;
            this.webApp.ready();
            this.isReady = true;
            resolve(this.webApp);
          }
        }, 100);

        setTimeout(() => {
          clearInterval(checkWebApp);
          if (!this.isReady) {
            reject(new Error('WebApp failed to load'));
          }
        }, 5000);
      } else {
        this.webApp = window.WebApp;
        this.webApp.ready();
        this.isReady = true;
        resolve(this.webApp);
      }
    });

    return this.initPromise;
  }

  getInstance() {
    return this.webApp;
  }

  getUser() {
    if (!this.webApp?.initDataUnsafe) {
      return null;
    }
    return this.webApp.initDataUnsafe.user || null;
  }

  getUserId() {
    const user = this.getUser();
    return user?.id || null;
  }

  getUserFirstName() {
    const user = this.getUser();
    return user?.first_name || '';
  }

  getUserLastName() {
    const user = this.getUser();
    return user?.last_name || '';
  }

  getUserFullName() {
    const firstName = this.getUserFirstName();
    const lastName = this.getUserLastName();
    return `${firstName} ${lastName}`.trim();
  }

  getUsername() {
    const user = this.getUser();
    return user?.username || null;
  }

  getPhotoUrl() {
    const user = this.getUser();
    return user?.photo_url || null;
  }

  getLanguageCode() {
    const user = this.getUser();
    return user?.language_code || 'ru';
  }

  getColorScheme() {
    return this.webApp?.colorScheme || 'light';
  }

  close() {
    if (this.webApp?.close) {
      this.webApp.close();
    }
  }

  showBackButton(onClick) {
    if (!this.webApp?.BackButton) return;
    
    this.webApp.BackButton.show();
    
    if (onClick) {
      this.webApp.BackButton.onClick(onClick);
    }
  }

  hideBackButton() {
    if (this.webApp?.BackButton) {
      this.webApp.BackButton.hide();
    }
  }

  enableClosingConfirmation() {
    if (this.webApp?.enableClosingConfirmation) {
      this.webApp.enableClosingConfirmation();
    }
  }

  disableClosingConfirmation() {
    if (this.webApp?.disableClosingConfirmation) {
      this.webApp.disableClosingConfirmation();
    }
  }
}

const webAppService = new WebAppService();

if (typeof window !== 'undefined') {
  webAppService.init().catch(console.error);
}

export default webAppService;
