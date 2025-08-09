import React from 'react';
import {createStackNavigator} from '@react-navigation/stack';
import WelcomeScreen from '../screens/WelcomeScreen';
import CustomerSelectScreen from '../screens/CustomerSelectScreen';
import InBodyScreen from '../screens/InBodyScreen';
import QuestionnaireScreen from '../screens/QuestionnaireScreen';
import CompletionScreen from '../screens/CompletionScreen';
import LoginScreen from '../screens/LoginScreen';
import {theme} from '../theme';

export type RootStackParamList = {
  Login: undefined;
  Welcome: undefined;
  CustomerSelect: undefined;
  InBody: {customerId: number};
  Questionnaire: {customerId: number; inbodyRecordId?: number};
  Completion: {responseId: number};
};

const Stack = createStackNavigator<RootStackParamList>();

const RootNavigator = () => {
  return (
    <Stack.Navigator
      initialRouteName="Login"
      screenOptions={{
        headerStyle: {
          backgroundColor: theme.colors.primary,
          elevation: 0,
          shadowOpacity: 0,
          height: 80,
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold',
          fontSize: 20,
        },
        cardStyle: {
          backgroundColor: theme.colors.background,
        },
      }}>
      <Stack.Screen
        name="Login"
        component={LoginScreen}
        options={{headerShown: false}}
      />
      <Stack.Screen
        name="Welcome"
        component={WelcomeScreen}
        options={{
          title: 'AIBIO 건강 문진',
          headerLeft: () => null,
        }}
      />
      <Stack.Screen
        name="CustomerSelect"
        component={CustomerSelectScreen}
        options={{title: '고객 선택'}}
      />
      <Stack.Screen
        name="InBody"
        component={InBodyScreen}
        options={{title: '인바디 측정'}}
      />
      <Stack.Screen
        name="Questionnaire"
        component={QuestionnaireScreen}
        options={{
          title: '건강 문진',
          headerLeft: () => null,
          gestureEnabled: false,
        }}
      />
      <Stack.Screen
        name="Completion"
        component={CompletionScreen}
        options={{
          title: '문진 완료',
          headerLeft: () => null,
          gestureEnabled: false,
        }}
      />
    </Stack.Navigator>
  );
};

export default RootNavigator;