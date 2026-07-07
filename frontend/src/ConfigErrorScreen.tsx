export default function ConfigErrorScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-stone-50 px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl shadow-elevated border border-stone-100 text-center">
        <h1 className="text-xl font-black text-brand-dark mb-2">TableWise isn't configured correctly</h1>
        <p className="text-stone-500 text-sm leading-relaxed">
          This deployment is missing its backend URL (<code className="font-mono text-xs bg-stone-100 px-1.5 py-0.5 rounded">VITE_API_BASE_URL</code>).
          If you're the site owner, set it in your hosting provider's environment
          variables and redeploy.
        </p>
      </div>
    </div>
  );
}
