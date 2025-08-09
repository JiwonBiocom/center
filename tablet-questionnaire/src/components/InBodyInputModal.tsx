import React, {useState} from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import {
  Modal,
  Portal,
  Text,
  TextInput,
  Button,
  Surface,
  IconButton,
  Divider,
  HelperText,
} from 'react-native-paper';
import {useDispatch} from 'react-redux';
import {setManualData} from '../store/slices/inbodySlice';
import {theme} from '../theme';

interface InBodyInputModalProps {
  visible: boolean;
  onDismiss: () => void;
  onComplete: () => void;
}

const InBodyInputModal: React.FC<InBodyInputModalProps> = ({
  visible,
  onDismiss,
  onComplete,
}) => {
  const dispatch = useDispatch();
  
  const [formData, setFormData] = useState({
    weight: '',
    height: '',
    body_fat_percentage: '',
    skeletal_muscle_mass: '',
    extracellular_water_ratio: '',
    phase_angle: '',
    visceral_fat_level: '',
  });
  
  const [errors, setErrors] = useState<{[key: string]: string}>({});

  const validateField = (field: string, value: string): string => {
    if (!value) return '';
    
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return '숫자를 입력해주세요';
    
    switch (field) {
      case 'weight':
        if (numValue < 20 || numValue > 300) return '20-300kg 범위로 입력해주세요';
        break;
      case 'height':
        if (numValue < 50 || numValue > 250) return '50-250cm 범위로 입력해주세요';
        break;
      case 'body_fat_percentage':
        if (numValue < 0 || numValue > 60) return '0-60% 범위로 입력해주세요';
        break;
      case 'phase_angle':
        if (numValue < 0 || numValue > 20) return '0-20 범위로 입력해주세요';
        break;
      case 'visceral_fat_level':
        if (numValue < 1 || numValue > 20) return '1-20 범위로 입력해주세요';
        break;
    }
    
    return '';
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({...prev, [field]: value}));
    
    // 실시간 유효성 검사
    const error = validateField(field, value);
    setErrors(prev => ({...prev, [field]: error}));
  };

  const handleSubmit = () => {
    // 전체 유효성 검사
    const newErrors: {[key: string]: string} = {};
    let hasError = false;
    
    // 필수 필드 검사
    if (!formData.weight) {
      newErrors.weight = '체중은 필수 입력입니다';
      hasError = true;
    }
    if (!formData.height) {
      newErrors.height = '키는 필수 입력입니다';
      hasError = true;
    }
    
    // 입력된 필드 유효성 검사
    Object.entries(formData).forEach(([field, value]) => {
      if (value) {
        const error = validateField(field, value);
        if (error) {
          newErrors[field] = error;
          hasError = true;
        }
      }
    });
    
    if (hasError) {
      setErrors(newErrors);
      return;
    }
    
    // 데이터 저장
    const inbodyData: any = {};
    Object.entries(formData).forEach(([field, value]) => {
      if (value) {
        inbodyData[field] = parseFloat(value);
      }
    });
    
    dispatch(setManualData(inbodyData));
    onComplete();
  };

  return (
    <Portal>
      <Modal
        visible={visible}
        onDismiss={onDismiss}
        contentContainerStyle={styles.modal}
        dismissable={false}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.keyboardView}>
          <Surface style={styles.surface}>
            <View style={styles.header}>
              <Text style={styles.title}>인바디 측정값 입력</Text>
              <IconButton
                icon="close"
                size={24}
                onPress={onDismiss}
              />
            </View>
            
            <Divider />
            
            <ScrollView style={styles.content}>
              <Text style={styles.sectionTitle}>필수 정보</Text>
              
              <TextInput
                label="체중 (kg) *"
                value={formData.weight}
                onChangeText={(value) => handleChange('weight', value)}
                keyboardType="decimal-pad"
                error={!!errors.weight}
                style={styles.input}
                mode="outlined"
              />
              <HelperText type="error" visible={!!errors.weight}>
                {errors.weight}
              </HelperText>
              
              <TextInput
                label="키 (cm) *"
                value={formData.height}
                onChangeText={(value) => handleChange('height', value)}
                keyboardType="decimal-pad"
                error={!!errors.height}
                style={styles.input}
                mode="outlined"
              />
              <HelperText type="error" visible={!!errors.height}>
                {errors.height}
              </HelperText>
              
              <Text style={[styles.sectionTitle, {marginTop: 20}]}>선택 정보</Text>
              
              <TextInput
                label="체지방률 (%)"
                value={formData.body_fat_percentage}
                onChangeText={(value) => handleChange('body_fat_percentage', value)}
                keyboardType="decimal-pad"
                error={!!errors.body_fat_percentage}
                style={styles.input}
                mode="outlined"
              />
              <HelperText type="error" visible={!!errors.body_fat_percentage}>
                {errors.body_fat_percentage}
              </HelperText>
              
              <TextInput
                label="골격근량 (kg)"
                value={formData.skeletal_muscle_mass}
                onChangeText={(value) => handleChange('skeletal_muscle_mass', value)}
                keyboardType="decimal-pad"
                error={!!errors.skeletal_muscle_mass}
                style={styles.input}
                mode="outlined"
              />
              <HelperText type="error" visible={!!errors.skeletal_muscle_mass}>
                {errors.skeletal_muscle_mass}
              </HelperText>
              
              <TextInput
                label="세포외수분비"
                value={formData.extracellular_water_ratio}
                onChangeText={(value) => handleChange('extracellular_water_ratio', value)}
                keyboardType="decimal-pad"
                error={!!errors.extracellular_water_ratio}
                style={styles.input}
                mode="outlined"
              />
              <HelperText type="error" visible={!!errors.extracellular_water_ratio}>
                {errors.extracellular_water_ratio}
              </HelperText>
              
              <TextInput
                label="위상각"
                value={formData.phase_angle}
                onChangeText={(value) => handleChange('phase_angle', value)}
                keyboardType="decimal-pad"
                error={!!errors.phase_angle}
                style={styles.input}
                mode="outlined"
              />
              <HelperText type="error" visible={!!errors.phase_angle}>
                {errors.phase_angle}
              </HelperText>
              
              <TextInput
                label="내장지방 레벨"
                value={formData.visceral_fat_level}
                onChangeText={(value) => handleChange('visceral_fat_level', value)}
                keyboardType="number-pad"
                error={!!errors.visceral_fat_level}
                style={styles.input}
                mode="outlined"
              />
              <HelperText type="error" visible={!!errors.visceral_fat_level}>
                {errors.visceral_fat_level}
              </HelperText>
            </ScrollView>
            
            <Divider />
            
            <View style={styles.actions}>
              <Button
                mode="outlined"
                onPress={onDismiss}
                style={styles.button}>
                취소
              </Button>
              <Button
                mode="contained"
                onPress={handleSubmit}
                style={styles.button}>
                저장
              </Button>
            </View>
          </Surface>
        </KeyboardAvoidingView>
      </Modal>
    </Portal>
  );
};

const styles = StyleSheet.create({
  modal: {
    margin: 20,
  },
  keyboardView: {
    flex: 1,
  },
  surface: {
    borderRadius: 12,
    overflow: 'hidden',
    maxHeight: '90%',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  content: {
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 12,
  },
  input: {
    marginBottom: 4,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    padding: 16,
    gap: 12,
  },
  button: {
    minWidth: 100,
  },
});

export default InBodyInputModal;