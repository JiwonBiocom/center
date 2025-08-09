import React, {useState} from 'react';
import {View, StyleSheet, ScrollView} from 'react-native';
import {
  Text,
  Surface,
  Button,
  Card,
  List,
  Divider,
  ActivityIndicator,
} from 'react-native-paper';
import {useNavigation, useRoute, RouteProp} from '@react-navigation/native';
import {StackNavigationProp} from '@react-navigation/stack';
import {useSelector, useDispatch} from 'react-redux';
import {RootState} from '../store';
import {setInBodyData} from '../store/slices/inbodySlice';
import InBodyInputModal from '../components/InBodyInputModal';
import {theme} from '../theme';
import type {RootStackParamList} from '../navigation/RootNavigator';

type InBodyScreenNavigationProp = StackNavigationProp<RootStackParamList, 'InBody'>;
type InBodyScreenRouteProp = RouteProp<RootStackParamList, 'InBody'>;

const InBodyScreen = () => {
  const navigation = useNavigation<InBodyScreenNavigationProp>();
  const route = useRoute<InBodyScreenRouteProp>();
  const dispatch = useDispatch();
  
  const {customerId} = route.params;
  const {currentData, isConnected, isLoading} = useSelector(
    (state: RootState) => state.inbody,
  );
  
  const [showManualInput, setShowManualInput] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleAutoConnect = async () => {
    setIsConnecting(true);
    // 인바디 기기 연결 시도 시뮬레이션
    setTimeout(() => {
      setIsConnecting(false);
      // 실제로는 Bluetooth/Wi-Fi 연결 로직
      alert('인바디 기기를 찾을 수 없습니다. 수동으로 입력해주세요.');
    }, 3000);
  };

  const handleManualInputComplete = () => {
    setShowManualInput(false);
    // 문진 화면으로 이동
    navigation.navigate('Questionnaire', {
      customerId,
      inbodyRecordId: undefined, // 실제로는 저장 후 ID 전달
    });
  };

  const handleSkip = () => {
    navigation.navigate('Questionnaire', {customerId});
  };

  const formatValue = (value?: number, unit: string = ''): string => {
    if (value === undefined || value === null) return '-';
    return `${value}${unit}`;
  };

  return (
    <ScrollView style={styles.container}>
      <Surface style={styles.content}>
        <Card style={styles.card}>
          <Card.Content>
            <Text style={styles.title}>인바디 측정</Text>
            <Text style={styles.subtitle}>
              정확한 건강 평가를 위해 인바디 측정을 권장합니다
            </Text>
          </Card.Content>
        </Card>

        {!currentData ? (
          <View style={styles.connectSection}>
            <Text style={styles.sectionTitle}>측정 방법 선택</Text>
            
            <Card style={styles.optionCard} onPress={handleAutoConnect}>
              <Card.Content style={styles.optionContent}>
                <List.Icon icon="bluetooth" color={theme.colors.primary} />
                <View style={styles.optionText}>
                  <Text style={styles.optionTitle}>인바디 기기 연결</Text>
                  <Text style={styles.optionSubtitle}>
                    블루투스로 인바디 기기와 자동 연결
                  </Text>
                </View>
              </Card.Content>
            </Card>

            <Card 
              style={styles.optionCard} 
              onPress={() => setShowManualInput(true)}>
              <Card.Content style={styles.optionContent}>
                <List.Icon icon="pencil" color={theme.colors.secondary} />
                <View style={styles.optionText}>
                  <Text style={styles.optionTitle}>수동 입력</Text>
                  <Text style={styles.optionSubtitle}>
                    측정값을 직접 입력합니다
                  </Text>
                </View>
              </Card.Content>
            </Card>
          </View>
        ) : (
          <View style={styles.dataSection}>
            <Text style={styles.sectionTitle}>측정 결과</Text>
            
            <Card style={styles.dataCard}>
              <Card.Content>
                <List.Item
                  title="체중"
                  description={formatValue(currentData.weight, 'kg')}
                  left={props => <List.Icon {...props} icon="scale" />}
                />
                <Divider />
                <List.Item
                  title="체지방률"
                  description={formatValue(currentData.body_fat_percentage, '%')}
                  left={props => <List.Icon {...props} icon="percent" />}
                />
                <Divider />
                <List.Item
                  title="골격근량"
                  description={formatValue(currentData.skeletal_muscle_mass, 'kg')}
                  left={props => <List.Icon {...props} icon="arm-flex" />}
                />
                <Divider />
                <List.Item
                  title="위상각"
                  description={formatValue(currentData.phase_angle, '°')}
                  left={props => <List.Icon {...props} icon="angle-acute" />}
                />
              </Card.Content>
            </Card>

            <View style={styles.dataActions}>
              <Button
                mode="outlined"
                onPress={() => setShowManualInput(true)}
                style={styles.actionButton}>
                다시 측정
              </Button>
              <Button
                mode="contained"
                onPress={handleManualInputComplete}
                style={styles.actionButton}>
                다음
              </Button>
            </View>
          </View>
        )}

        <View style={styles.footer}>
          <Button
            mode="text"
            onPress={handleSkip}
            style={styles.skipButton}>
            인바디 측정 건너뛰기
          </Button>
        </View>
      </Surface>

      {isConnecting && (
        <View style={styles.loadingOverlay}>
          <Surface style={styles.loadingCard}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <Text style={styles.loadingText}>인바디 기기 연결 중...</Text>
          </Surface>
        </View>
      )}

      <InBodyInputModal
        visible={showManualInput}
        onDismiss={() => setShowManualInput(false)}
        onComplete={handleManualInputComplete}
      />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    margin: 24,
    borderRadius: 16,
    padding: 24,
  },
  card: {
    marginBottom: 24,
    elevation: 2,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    lineHeight: 22,
  },
  connectSection: {
    marginTop: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 16,
  },
  optionCard: {
    marginBottom: 16,
    elevation: 2,
  },
  optionContent: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
  },
  optionText: {
    flex: 1,
    marginLeft: 16,
  },
  optionTitle: {
    fontSize: 18,
    fontWeight: '500',
    color: theme.colors.text,
    marginBottom: 4,
  },
  optionSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
  dataSection: {
    marginTop: 16,
  },
  dataCard: {
    elevation: 2,
  },
  dataActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
    gap: 16,
  },
  actionButton: {
    flex: 1,
  },
  footer: {
    marginTop: 32,
    alignItems: 'center',
  },
  skipButton: {
    paddingHorizontal: 24,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingCard: {
    padding: 32,
    borderRadius: 16,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: theme.colors.text,
  },
});

export default InBodyScreen;