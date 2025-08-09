/**
 * AIBIO 태블릿 문진 앱
 */
import React from 'react';
import {Provider as ReduxProvider} from 'react-redux';
import {Provider as PaperProvider} from 'react-native-paper';
import {NavigationContainer} from '@react-navigation/native';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {store} from './src/store';
import {theme} from './src/theme';
import RootNavigator from './src/navigation/RootNavigator';
import {OfflineSyncProvider} from './src/contexts/OfflineSyncContext';

const App = () => {
  return (
    <ReduxProvider store={store}>
      <PaperProvider theme={theme}>
        <SafeAreaProvider>
          <OfflineSyncProvider>
            <NavigationContainer>
              <RootNavigator />
            </NavigationContainer>
          </OfflineSyncProvider>
        </SafeAreaProvider>
      </PaperProvider>
    </ReduxProvider>
  );
};

export default App;