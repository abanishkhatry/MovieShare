import React from 'react'; // React library for component-based UI
import { View, Text, StyleSheet } from 'react-native'; // Native components
import { COLORS, FONT_SIZES } from './styles/global'; 

export default function App() {
  return (
    <View style={styles.container}>  {/* View is like a <div> */}
      <Text style= {styles.welcome}> Welcome to MovieShare 🎬</Text>
    </View>
  );
}

const styles = StyleSheet.create({ // Styling like CSS-in-JS
  container: {
    flex: 1, // Takes full screen
    justifyContent: 'center', // Centers vertically
    alignItems: 'center', // Centers horizontally
  },
  welcome: {
    fontSize: FONT_SIZES.lg,
    color: COLORS.primary,
  },
});

