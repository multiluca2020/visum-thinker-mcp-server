// Script per avviare istanza Visum persistente in background
import { PersistentVisumController } from './build/persistent-visum-controller.js';

console.log('🚀 Starting Visum persistent instance in background...');

const controller = PersistentVisumController.getInstance();

try {
  const result = await controller.startPersistentVisumProcess();
  
  if (result.success) {
    console.log('✅ Visum instance started successfully!');
    console.log(`📊 Network: ${result.nodes} nodes, ${result.links} links, ${result.zones} zones`);
    console.log('🔄 Instance is now running in background and ready for commands...');
    console.log('💡 Use other scripts to send commands to this persistent instance');
    
    // Mantieni il processo attivo
    console.log('🔄 Keeping process alive for background operation...');
    setInterval(() => {
      // Noop - mantiene il processo Node.js attivo
    }, 30000);
    
  } else {
    console.log('❌ Failed to start:', result.message);
    process.exit(1);
  }
  
} catch (error) {
  console.error('❌ Error:', error.message);
  process.exit(1);
}