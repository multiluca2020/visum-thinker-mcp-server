import net from 'net';

const client = new net.Socket();

console.log('🔍 Test connessione server Visum TCP');
console.log('📍 Porta: 7906');
console.log('');

client.connect(7906, '::1', () => {
    console.log('✅ Connesso al server sulla porta 7906!');
});

client.on('data', (data) => {
    const response = JSON.parse(data.toString());
    console.log('📥 Risposta server:');
    console.log(JSON.stringify(response, null, 2));
    client.destroy();
});

client.on('close', () => {
    console.log('\n🔌 Connessione chiusa');
});

client.on('error', (err) => {
    console.error('❌ Errore:', err.message);
});

setTimeout(() => {
    console.log('\n⏰ Timeout - chiusura...');
    client.destroy();
}, 5000);
