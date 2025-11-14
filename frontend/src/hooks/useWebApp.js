import { useState, useEffect, useCallback } from 'react';
import webAppService from '../services/webApp';

export const useWebApp = () => {
  const [webApp, setWebApp] = useState(null);
  const [user, setUser] = useState(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    webAppService.init()
      .then((instance) => {
        setWebApp(instance);
        setUser(webAppService.getUser());
        setIsReady(true);
      })
      .catch((error) => {
        console.error('Failed to initialize WebApp:', error);
        setIsReady(true);
      });
  }, []);

  return {
    webApp,
    user,
    isReady,
    userId: user?.id || 97092446,
    firstName: user?.first_name || '',
    lastName: user?.last_name || '',
    username: user?.username,
    photoUrl: user?.photo_url,
    languageCode: user?.language_code || 'ru',
  };
};

export const useWebAppTheme = () => {
  const [colorScheme, setColorScheme] = useState('light');

  useEffect(() => {
    webAppService.init()
      .then(() => {
        setColorScheme(webAppService.getColorScheme());
      })
      .catch(console.error);
  }, []);

  return {
    colorScheme,
    isDark: colorScheme === 'dark',
  };
};

export const useBackButton = (onClick, options = {}) => {
  const { visible = true } = options;

  useEffect(() => {
    if (!visible) {
      webAppService.hideBackButton();
      return;
    }

    webAppService.showBackButton(onClick);

    return () => {
      webAppService.hideBackButton();
    };
  }, [onClick, visible]);
};