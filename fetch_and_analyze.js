const https = require('https');
const fs = require('fs');

async function fetchPage(page) {
  return new Promise((resolve, reject) => {
    const url = `https://api-leaderboard.autoppia.com/api/v1/tasks/search?successMode=all&page=${page}&limit=100&includeDetails=false`;
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const obj = JSON.parse(data);
          resolve(obj.data.tasks || []);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function main() {
  const allTasks = [];
  let page = 1;
  let hasMore = true;

  // Fetch all pages
  while (hasMore) {
    try {
      const tasks = await fetchPage(page);
      if (tasks.length === 0) {
        hasMore = false;
      } else {
        allTasks.push(...tasks);
        page++;
        if (page > 50) hasMore = false; // Safety limit
      }
    } catch (e) {
      hasMore = false;
    }
  }

  // Analysis
  const completed = allTasks.filter(t => t.status === 'completed');
  const failed = allTasks.filter(t => t.status === 'failed');

  const useCases = {};
  allTasks.forEach(t => {
    useCases[t.useCase] = (useCases[t.useCase] || 0) + 1;
  });

  const durations = allTasks.map(t => t.duration).sort((a, b) => a - b);
  const websites = {};
  allTasks.forEach(t => {
    const url = new URL(t.website);
    const host = url.hostname + ':' + url.port;
    websites[host] = (websites[host] || 0) + 1;
  });

  const failureReasons = {};
  failed.forEach(t => {
    const reason = t.zeroReason || 'unknown';
    failureReasons[reason] = (failureReasons[reason] || 0) + 1;
  });

  const miners = {};
  allTasks.forEach(t => {
    if (!miners[t.minerName]) miners[t.minerName] = { total: 0, completed: 0 };
    miners[t.minerName].total++;
    if (t.status === 'completed') miners[t.minerName].completed++;
  });

  const validators = {};
  allTasks.forEach(t => {
    if (!validators[t.validatorName]) validators[t.validatorName] = { total: 0, completed: 0 };
    validators[t.validatorName].total++;
    if (t.status === 'completed') validators[t.validatorName].completed++;
  });

  // Output analysis
  console.log('=== COMPREHENSIVE EVALUATION DATA ANALYSIS ===\n');
  console.log('1. TOTAL DATASET STATISTICS:');
  console.log(`   Total tasks: ${allTasks.length}`);
  console.log(`   Total pages fetched: ${page - 1}`);

  console.log('\n2. SUCCESS vs FAILURE BREAKDOWN:');
  console.log(`   Completed: ${completed.length} (${(completed.length/allTasks.length*100).toFixed(2)}%)`);
  console.log(`   Failed: ${failed.length} (${(failed.length/allTasks.length*100).toFixed(2)}%)`);

  const scores = {};
  allTasks.forEach(t => {
    scores[t.score] = (scores[t.score] || 0) + 1;
  });
  console.log('\n3. SCORE DISTRIBUTION:');
  Object.keys(scores).sort().forEach(score => {
    console.log(`   Score ${score}: ${scores[score]} tasks`);
  });

  console.log('\n4. UNIQUE TASK TYPES (Total: ' + Object.keys(useCases).length + '):');
  Object.entries(useCases).sort((a,b) => b[1]-a[1]).slice(0, 40).forEach(([uc, count]) => {
    const taskData = allTasks.find(t => t.useCase === uc);
    const taskStatus = taskData.status === 'completed' ? 'PASS' : 'FAIL';
    console.log(`   ${uc}: ${count} (${taskStatus})`);
  });

  console.log('\n5. DURATION STATISTICS (seconds):');
  console.log(`   Min: ${Math.min(...durations)}`);
  console.log(`   Max: ${Math.max(...durations)}`);
  console.log(`   Average: ${(durations.reduce((a,b)=>a+b)/durations.length).toFixed(2)}`);
  console.log(`   Median: ${durations[Math.floor(durations.length/2)]}`);
  console.log(`   95th percentile: ${durations[Math.floor(durations.length*0.95)]}`);

  console.log('\n6. WEBSITES/PLATFORMS TESTED:');
  Object.entries(websites).sort((a,b) => b[1]-a[1]).forEach(([site, count]) => {
    console.log(`   ${site}: ${count} tests`);
  });

  console.log('\n7. FAILURE REASONS:');
  Object.entries(failureReasons).sort((a,b) => b[1]-a[1]).forEach(([reason, count]) => {
    console.log(`   ${reason}: ${count} failures`);
  });

  console.log('\n8. TOP PERFORMING MINERS (Top 30):');
  Object.entries(miners).sort((a,b) => (b[1].completed/b[1].total) - (a[1].completed/a[1].total))
    .slice(0, 30).forEach(([name, stats]) => {
    const rate = (stats.completed/stats.total*100).toFixed(2);
    console.log(`   ${name}: ${stats.completed}/${stats.total} (${rate}%)`);
  });

  console.log('\n9. VALIDATOR DISTRIBUTION:');
  Object.entries(validators).sort((a,b) => b[1].total - a[1].total).forEach(([name, stats]) => {
    const rate = (stats.completed/stats.total*100).toFixed(2);
    console.log(`   ${name}: ${stats.total} evaluations (${stats.completed} completed, ${rate}%)`);
  });

  console.log('\n10. SAMPLE FAILED TASKS:');
  failed.slice(0, 20).forEach((task, i) => {
    console.log(`\n   ${i+1}. ${task.useCase}`);
    console.log(`      Website: ${task.website.split('?')[0]}`);
    console.log(`      Prompt: ${task.prompt.substring(0, 100)}`);
    console.log(`      Duration: ${task.duration}s`);
    console.log(`      Failure reason: ${task.zeroReason || 'unknown'}`);
  });

  // Save raw data to file for reference
  fs.writeFileSync('tasks_summary.json', JSON.stringify({
    totalTasks: allTasks.length,
    completedTasks: completed.length,
    failedTasks: failed.length,
    successRate: (completed.length/allTasks.length*100).toFixed(2),
    uniqueTaskTypes: Object.keys(useCases).length,
    averageDuration: (durations.reduce((a,b)=>a+b)/durations.length).toFixed(2),
    websites: Object.keys(websites).length,
    uniqueMiners: Object.keys(miners).length,
    uniqueValidators: Object.keys(validators).length,
    topMiner: Object.entries(miners).sort((a,b) => (b[1].completed/b[1].total) - (a[1].completed/a[1].total))[0],
  }, null, 2));

  console.log('\n\nSummary saved to tasks_summary.json');
}

main().catch(console.error);
