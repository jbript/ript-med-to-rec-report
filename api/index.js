export default function handler(req, res) {
    res.status(200).json({
        service: 'RIPT Cannabis Reporting API',
        status: 'active',
        message: 'API is working!',
        timestamp: new Date().toISOString()
    });
}
