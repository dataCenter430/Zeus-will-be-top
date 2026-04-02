const https = require('https');

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

  while (page <= 46) {
    const tasks = await fetchPage(page);
    if (tasks.length === 0) break;
    allTasks.push(...tasks);
    page++;
  }

  const failed = allTasks.filter(t => t.status === 'failed');
  const completed = allTasks.filter(t => t.status === 'completed');

  // Analyze failure patterns by task type
  const failurePatterns = {};
  failed.forEach(t => {
    if (!failurePatterns[t.useCase]) {
      failurePatterns[t.useCase] = { count: 0, durations: [], reasons: {} };
    }
    failurePatterns[t.useCase].count++;
    failurePatterns[t.useCase].durations.push(t.duration);
    failurePatterns[t.useCase].reasons[t.zeroReason || 'unknown'] = 
      (failurePatterns[t.useCase].reasons[t.zeroReason || 'unknown'] || 0) + 1;
  });

  // Analyze success patterns by task type
  const successPatterns = {};
  completed.forEach(t => {
    if (!successPatterns[t.useCase]) {
      successPatterns[t.useCase] = { count: 0, durations: [] };
    }
    successPatterns[t.useCase].count++;
    successPatterns[t.useCase].durations.push(t.duration);
  });

  console.log('=== DETAILED FAILURE PATTERN ANALYSIS ===\n');
  
  console.log('TASKS THAT FAIL MOST (Top 20):');
  Object.entries(failurePatterns)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 20)
    .forEach(([task, data], i) => {
      const avgDur = (data.durations.reduce((a,b)=>a+b)/data.durations.length).toFixed(1);
      console.log(`\n  ${i+1}. ${task}: ${data.count} failures (avg ${avgDur}s)`);
      Object.entries(data.reasons).forEach(([reason, count]) => {
        console.log(`     - ${reason}: ${count}`);
      });
    });

  console.log('\n\nTASKS THAT SUCCEED MOST (Top 20):');
  Object.entries(successPatterns)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 20)
    .forEach(([task, data], i) => {
      const avgDur = (data.durations.reduce((a,b)=>a+b)/data.durations.length).toFixed(1);
      console.log(`  ${i+1}. ${task}: ${data.count} successes (avg ${avgDur}s)`);
    });

  // Sample prompts from different categories
  console.log('\n\n=== SAMPLE TASK PROMPTS ===\n');
  
  console.log('SAMPLE FAILING TASK PROMPTS:');
  const uniqueFailingTasks = {};
  failed.forEach(t => {
    if (!uniqueFailingTasks[t.useCase]) {
      uniqueFailingTasks[t.useCase] = t;
    }
  });
  Object.entries(uniqueFailingTasks).slice(0, 15).forEach(([task, data], i) => {
    console.log(`\n  ${i+1}. ${task}`);
    console.log(`     Website: ${data.website.split('?')[0]}`);
    console.log(`     Prompt: "${data.prompt.substring(0, 140)}"`);
  });

  console.log('\n\nSAMPLE SUCCEEDING TASK PROMPTS:');
  const uniqueSuccessTasks = {};
  completed.forEach(t => {
    if (!uniqueSuccessTasks[t.useCase]) {
      uniqueSuccessTasks[t.useCase] = t;
    }
  });
  Object.entries(uniqueSuccessTasks).slice(0, 15).forEach(([task, data], i) => {
    console.log(`\n  ${i+1}. ${task}`);
    console.log(`     Website: ${data.website.split('?')[0]}`);
    console.log(`     Prompt: "${data.prompt.substring(0, 140)}"`);
  });

  // Complexity analysis
  console.log('\n\n=== TASK COMPLEXITY ANALYSIS ===\n');
  
  // Count conditions in prompts
  const complexityByTask = {};
  allTasks.forEach(t => {
    if (!complexityByTask[t.useCase]) {
      complexityByTask[t.useCase] = { 
        total: 0, 
        passed: 0, 
        avgConditions: 0, 
        conditions: []
      };
    }
    const conditionCount = (t.prompt.match(/where|and|or|contains|equals|greater|less|not/gi) || []).length;
    complexityByTask[t.useCase].conditions.push(conditionCount);
    complexityByTask[t.useCase].avgConditions = 
      complexityByTask[t.useCase].conditions.reduce((a,b)=>a+b) / complexityByTask[t.useCase].conditions.length;
    complexityByTask[t.useCase].total++;
    if (t.status === 'completed') complexityByTask[t.useCase].passed++;
  });

  console.log('TASKS BY COMPLEXITY (avg condition keywords):');
  Object.entries(complexityByTask)
    .sort((a, b) => b[1].avgConditions - a[1].avgConditions)
    .slice(0, 15)
    .forEach(([task, data]) => {
      const successRate = (data.passed / data.total * 100).toFixed(1);
      console.log(`  ${task}: ${data.avgConditions.toFixed(1)} avg conditions, ${successRate}% success`);
    });

}

main().catch(console.error);
