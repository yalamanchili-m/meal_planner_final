import { useState } from 'react';

export default function MetricsForm({ onSubmit, error }) {
  const [formData, setFormData] = useState({
    height: 170,
    weight: 65,
    age: 25,
    gender: 'male',
    goal: 'maintain',
  });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit({
      ...formData,
      height: Number(formData.height),
      weight: Number(formData.weight),
      age: Number(formData.age),
    });
  };

  return (
    <form onSubmit={handleSubmit} className="w-full rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-md sm:p-8">
      <div className="mb-6">
        <p className="text-xs font-medium uppercase tracking-widest text-slate-500">Form</p>
        <h2 className="mt-2 text-2xl font-semibold text-slate-900">Enter your details</h2>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <label className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="mb-1 text-sm font-medium text-slate-700">Height</p>
          <span className="text-xs text-slate-500">In cm</span>
          <input
            type="number"
            name="height"
            value={formData.height}
            onChange={handleChange}
            className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 outline-none focus:border-indigo-500"
          />
        </label>

        <label className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="mb-1 text-sm font-medium text-slate-700">Weight</p>
          <span className="text-xs text-slate-500">In kg</span>
          <input
            type="number"
            name="weight"
            value={formData.weight}
            onChange={handleChange}
            className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 outline-none focus:border-indigo-500"
          />
        </label>

        <label className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="mb-1 text-sm font-medium text-slate-700">Age</p>
          <span className="text-xs text-slate-500">In years</span>
          <input
            type="number"
            name="age"
            value={formData.age}
            onChange={handleChange}
            className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 outline-none focus:border-indigo-500"
          />
        </label>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <label className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="mb-1 text-sm font-medium text-slate-700">Gender</p>
          <select
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 outline-none focus:border-indigo-500"
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </label>

        <label className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <p className="mb-1 text-sm font-medium text-slate-700">Goal</p>
          <select
            name="goal"
            value={formData.goal}
            onChange={handleChange}
            className="mt-3 w-full rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm text-slate-900 outline-none focus:border-indigo-500"
          >
            <option value="weight_loss">Lose weight</option>
            <option value="maintain">Maintain</option>
            <option value="weight_gain">Gain weight</option>
          </select>
        </label>
      </div>

      {error ? (
        <div className="mt-5 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="submit"
          className="w-full rounded-2xl bg-indigo-600 px-6 py-3 text-sm font-medium text-white shadow-md transition-all hover:bg-indigo-700 hover:shadow-lg"
        >
          Create plan
        </button>
        <button
          type="button"
          onClick={() =>
            setFormData({
              height: 170,
              weight: 65,
              age: 25,
              gender: 'male',
              goal: 'maintain',
            })
          }
          className="w-full rounded-2xl border border-slate-200 bg-white px-6 py-3 text-sm font-medium text-slate-700 shadow-sm transition-all hover:bg-slate-50 hover:shadow-md"
        >
          Reset form
        </button>
      </div>
    </form>
  );
}
