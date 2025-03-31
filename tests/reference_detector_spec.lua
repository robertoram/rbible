local reference_detector = require('rbible.reference_detector')

describe('reference_detector', function()
  it('should detect simple references', function()
    local refs = reference_detector.detect_references('Juan 3:16')
    assert.are.equal(1, #refs)
    assert.are.equal('Juan 3:16', refs[1].reference)
  end)

  it('should handle multiple references', function()
    local refs = reference_detector.detect_references('Salmos 23:1 y Juan 3:16')
    assert.are.equal(2, #refs)
    assert.are.equal('Salmos 23:1', refs[1].reference)
    assert.are.equal('Juan 3:16', refs[2].reference)
  end)

  it('should handle numbered books', function()
    local refs = reference_detector.detect_references('1 Reyes 19:11')
    assert.are.equal(1, #refs)
    assert.are.equal('1 Reyes 19:11', refs[1].reference)
  end)

  it('should handle verse ranges', function()
    local refs = reference_detector.detect_references('Salmos 23:1-6')
    assert.are.equal(1, #refs)
    assert.are.equal('Salmos 23:1-6', refs[1].reference)
  end)

  it('should handle accented characters', function()
    local refs = reference_detector.detect_references('Génesis 1:1')
    assert.are.equal(1, #refs)
    assert.are.equal('Génesis 1:1', refs[1].reference)
  end)

  it('should ignore invalid references', function()
    local refs = reference_detector.detect_references('Not a reference')
    assert.are.equal(0, #refs)
  end)

  it('should handle references with extra spaces', function()
    local refs = reference_detector.detect_references('  Salmos   23:1  ')
    assert.are.equal(1, #refs)
    assert.are.equal('Salmos 23:1', refs[1].reference)
  end)
end)