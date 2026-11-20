import assert from 'node:assert/strict';
const base = process.env.RECYCLEHUB_URL || 'http://127.0.0.1:8000';
function client() {
    const jar = new Map();
    let version;
    return async (path, { method = 'GET', data, csrf = true, inertia = false } = {}) => {
        const headers = { Accept: inertia ? 'text/html' : 'application/json', Cookie: [...jar].map(([k,v]) => k + '=' + v).join('; ') };
        if (inertia) headers['X-Inertia'] = 'true';
        if (inertia && version) headers['X-Inertia-Version'] = version;
        if (csrf && jar.has('XSRF-TOKEN')) headers['X-XSRF-TOKEN'] = decodeURIComponent(jar.get('XSRF-TOKEN'));
        if (data) headers['Content-Type'] = 'application/x-www-form-urlencoded';
        const r = await fetch(base + path, { method, headers, body: data ? new URLSearchParams(data) : undefined, redirect: 'manual' });
        for (const cookie of r.headers.getSetCookie()) {
            const part = cookie.split(';')[0]; const at = part.indexOf('=');
            jar.set(part.slice(0, at), part.slice(at + 1));
        }
        const text = await r.text();
        const page = text.match(/data-page="([^"]+)"/);
        if (page) version = JSON.parse(page[1].replaceAll('&quot;', '"').replaceAll('&amp;', '&').replaceAll('&#039;', "'")).version;
        let json; try { json = JSON.parse(text); } catch { json = null; }
        return { status: r.status, json, location: r.headers.get('location') };
    };
}
const guest = client();
assert.equal((await guest('/dashboard')).status, 401);
const nasabah = client();
assert.equal((await nasabah('/login')).status, 200);
assert.equal((await nasabah('/login', { method: 'POST', data: { email: 'nasabah1@recyclehub.test', password: 'Recycle123!' } })).status, 200);
const dashboard = await nasabah('/dashboard', { inertia: true });
assert.equal(dashboard.status, 200);
assert.equal(dashboard.json.props.auth.user.role, 'nasabah');
const mine = await nasabah('/setoran');
assert.equal(mine.status, 200);
assert.ok(mine.json.items.every(i => i.user_id === dashboard.json.props.auth.user.id));
assert.equal((await nasabah('/setoran', { method: 'POST', csrf: false, data: {} })).status, 419);
assert.equal((await nasabah('/setoran', { method: 'POST', data: {} })).status, 422);
assert.equal((await nasabah('/katalog', { method: 'POST', data: {} })).status, 403);
const admin = client();
await admin('/login');
assert.equal((await admin('/login', { method: 'POST', data: { email: 'admin@recyclehub.test', password: 'Recycle123!' } })).status, 200);
const all = await admin('/setoran');
assert.equal(all.status, 200);
const other = all.json.items.find(i => i.user_id !== dashboard.json.props.auth.user.id);
assert.ok(other, 'Seeder must contain another nasabah transaction');
assert.equal((await nasabah('/setoran/' + other.id)).status, 403);
assert.equal((await admin('/setoran', { method: 'POST', data: {} })).status, 403);
assert.equal((await nasabah('/logout', { method: 'POST' })).status, 204);
assert.equal((await nasabah('/dashboard')).status, 401);
console.log('HTTP smoke passed: MySQL sessions, login/logout, Inertia pages, scoped JSON, CSRF 419, validation 422, authorization 403.');
