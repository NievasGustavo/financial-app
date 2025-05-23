export default function Login() {
  return (
    <div className="flex flex-col items-center justify-center h-screen">
      <h1>Login</h1>
      <form method="post" className="flex flex-col gap-6 p-5">
        <fieldset className="fieldset">
          <legend className="fieldset-legend">Username:</legend>
          <input
            className="input input-primary"
            type="email"
            name="email"
            placeholder="Email"
          />
        </fieldset>
        <fieldset className="fieldset">
          <legend className="fieldset-legend">Password:</legend>
          <input
            className="input input-primary"
            type="password"
            name="password"
            placeholder="Password"
          />
        </fieldset>

        <button type="submit" className="btn btn-primary">
          Sign In
        </button>
      </form>
    </div>
  );
}
