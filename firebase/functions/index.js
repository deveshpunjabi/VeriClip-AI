const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

exports.onThreatCreated = functions.firestore
  .document('threats/{threatId}')
  .onCreate(async (snap, context) => {
    const threat = snap.data();
    console.log(`New threat created: ${context.params.threatId}`);
    
    // Send notification to admins
    await admin.messaging().sendToTopic('admin_alerts', {
      notification: {
        title: 'New Threat Detected',
        body: `Threat level: ${threat.threat_level}`,
      },
      data: { threat_id: context.params.threatId },
    });
    
    return null;
  });

exports.generateTakedownPDF = functions.https.onCall(async (data, context) => {
  // TODO: Implement PDF generation
  return { success: true, message: 'PDF generation pending' };
});

exports.auditLogger = functions.firestore
  .document('audit_logs/{logId}')
  .onWrite((change, context) => {
    console.log(`Audit log: ${context.params.logId}`);
    return null;
  });
