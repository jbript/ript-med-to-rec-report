export default function handler(req, res) {
    res.setHeader('Content-Type', 'application/json');
    res.status(200).json({
        service: 'RIPT Med to Rec Report API',
        status: 'active',
        message: 'Cannabis reporting API is working!',
        timestamp: new Date().toISOString(),
        nodeVersion: process.version
    });
}
